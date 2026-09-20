import ipaddress
import json
import logging
import re
import socket
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from django.conf import settings

logger = logging.getLogger(__name__)

MAX_PAGE_SIZE = 5 * 1024 * 1024  # 5 MB
MAX_TEXT_CHARS = 25000
FETCH_TIMEOUT = (5, 12)  # (connect, read) seconds

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


class ExtractionConfigError(Exception):
    """Raised when configuration for extraction (e.g. API key) is missing."""



class ExtractionError(Exception):
    """Raised when page extraction or parsing fails."""



def validate_url(url: str) -> str:
    """
    Validates URL format and protects against SSRF attacks by blocking
    access to loopback, private, link-local, or reserved IP addresses.
    """
    if not url or not isinstance(url, str):
        raise ExtractionError("A valid URL string is required.")

    parsed = urlparse(url.strip())
    if parsed.scheme not in ("http", "https"):
        raise ExtractionError("Only http and https protocols are supported.")

    hostname = parsed.hostname
    if not hostname:
        raise ExtractionError("Invalid URL host.")

    try:
        addr_info = socket.getaddrinfo(hostname, None)
    except socket.gaierror as exc:
        raise ExtractionError(f"Could not resolve host '{hostname}': {exc}")

    for family, _, _, _, sockaddr in addr_info:
        ip_str = sockaddr[0]
        try:
            ip = ipaddress.ip_address(ip_str)
        except ValueError:
            continue

        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
            or not ip.is_global
        ):
            raise ExtractionError(
                "Access to internal, private, or reserved network addresses is not allowed."
            )

    return parsed.geturl()


def fetch_html(url: str) -> str:
    """
    Downloads HTML content from a URL safely with size and timeout limits.
    """
    headers = {
        "User-Agent": DEFAULT_USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,fr;q=0.8",
    }

    try:
        with requests.get(
            url, headers=headers, timeout=FETCH_TIMEOUT, stream=True
        ) as response:
            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "")
            if content_type and not any(
                t in content_type.lower()
                for t in ("text/html", "application/xhtml+xml", "text/plain")
            ):
                raise ExtractionError("The requested URL does not return HTML content.")

            raw_bytes = bytearray()
            for chunk in response.iter_content(chunk_size=16384):
                raw_bytes.extend(chunk)
                if len(raw_bytes) > MAX_PAGE_SIZE:
                    raise ExtractionError("Webpage is too large to process.")

            encoding = response.encoding or "utf-8"
            try:
                return raw_bytes.decode(encoding, errors="replace")
            except Exception:
                return raw_bytes.decode("utf-8", errors="replace")
    except requests.RequestException as exc:
        logger.warning("Error fetching URL %s: %s", url, exc)
        raise ExtractionError(f"Unable to download webpage: {exc}")


def _find_recipe_json_ld(soup: BeautifulSoup):
    """
    Finds Schema.org Recipe data in JSON-LD script elements if available.
    """
    scripts = soup.find_all("script", type="application/ld+json")
    for script in scripts:
        if not script.string:
            continue
        try:
            data = json.loads(script.string)
        except Exception:
            continue

        candidate = _search_recipe_in_object(data)
        if candidate:
            return candidate
    return None


def _search_recipe_in_object(obj):
    """
    Recursively searches for an object with @type == 'Recipe' or containing 'Recipe'.
    """
    if isinstance(obj, list):
        for item in obj:
            res = _search_recipe_in_object(item)
            if res:
                return res
    elif isinstance(obj, dict):
        obj_type = obj.get("@type")
        if (isinstance(obj_type, str) and obj_type.lower() == "recipe") or (
            isinstance(obj_type, list)
            and any(isinstance(t, str) and t.lower() == "recipe" for t in obj_type)
        ):
            return obj

        # Check @graph
        if "@graph" in obj and isinstance(obj["@graph"], list):
            for item in obj["@graph"]:
                res = _search_recipe_in_object(item)
                if res:
                    return res

        for v in obj.values():
            if isinstance(v, (dict, list)):
                res = _search_recipe_in_object(v)
                if res:
                    return res
    return None


def extract_recipe_payload(html: str) -> tuple:
    """
    Parses HTML and returns either a compact JSON string representing Schema.org Recipe
    (is_json_ld=True) or cleaned readable page text (is_json_ld=False).
    """
    soup = BeautifulSoup(html, "html.parser")

    # 1. Look for Schema.org Recipe JSON-LD
    json_ld_recipe = _find_recipe_json_ld(soup)
    if json_ld_recipe:
        # Keep only relevant fields to reduce token usage
        relevant_keys = (
            "name",
            "headline",
            "description",
            "recipeIngredient",
            "ingredients",
            "recipeInstructions",
            "step",
        )
        compact = {k: json_ld_recipe[k] for k in relevant_keys if k in json_ld_recipe}
        if compact:
            return json.dumps(compact, ensure_ascii=False), True

    # 2. Fallback: Clean HTML and extract visible text
    for tag in soup(
        [
            "script",
            "style",
            "nav",
            "footer",
            "header",
            "aside",
            "noscript",
            "iframe",
            "svg",
        ]
    ):
        tag.decompose()

    text = soup.get_text(separator="\n")
    # Collapse multiple whitespace / empty lines
    lines = [line.strip() for line in text.splitlines()]
    clean_lines = [line for line in lines if line]
    clean_text = "\n".join(clean_lines)

    if len(clean_text) > MAX_TEXT_CHARS:
        clean_text = clean_text[:MAX_TEXT_CHARS]

    if not clean_text.strip():
        raise ExtractionError("No readable content could be found on the page.")

    return clean_text, False


def _parse_gemini_json_response(data: dict) -> dict:
    """
    Parses JSON output from either the Interactions API (steps / output_text)
    or legacy generateContent (candidates / parts).
    """
    text = ""
    if isinstance(data.get("output_text"), str) and data["output_text"].strip():
        text = data["output_text"]

    if not text and isinstance(data.get("steps"), list):
        for step in reversed(data["steps"]):
            if isinstance(step, dict):
                if step.get("type") == "model_output":
                    content = step.get("content")
                    if isinstance(content, list):
                        parts = [
                            c.get("text", "")
                            for c in content
                            if isinstance(c, dict) and "text" in c
                        ]
                        if parts:
                            text = "".join(parts)
                            break
                    elif isinstance(content, str) and content.strip():
                        text = content
                        break
                elif "text" in step and isinstance(step["text"], str):
                    text = step["text"]
                    break

    if not text and isinstance(data.get("candidates"), list) and data["candidates"]:
        parts = data["candidates"][0].get("content", {}).get("parts", [])
        if parts and isinstance(parts[0], dict):
            text = parts[0].get("text", "")

    if not text:
        raise ExtractionError("No response content received from Gemini API.")

    cleaned_text = text.strip()
    if cleaned_text.startswith("```"):
        cleaned_text = re.sub(r"^```(?:json)?\n?", "", cleaned_text)
        cleaned_text = re.sub(r"\n?```$", "", cleaned_text).strip()

    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError as exc:
        logger.error(
            "Failed to parse JSON from Gemini text: %s | Text: %s",
            exc,
            cleaned_text[:300],
        )
        raise ExtractionError("Failed to parse recipe data from Gemini API response.")


def call_gemini_api(content: str, is_json_ld: bool) -> dict:
    """
    Sends the extracted recipe content to Google Gemini API using the Interactions API
    (/v1beta/interactions) with structured JSON schema and legacy fallback.
    """
    api_key = getattr(settings, "GEMINI_API_KEY", "")
    if not api_key:
        raise ExtractionConfigError(
            "Gemini API key is not configured. Please set GEMINI_API_KEY in your environment."
        )

    model = getattr(settings, "GEMINI_MODEL", "")
    if not model:
        raise ExtractionConfigError(
            "Gemini model not configured. Please set GEMINI_MODEL in your environment."
        )
    content_type_desc = "Schema.org JSON-LD data" if is_json_ld else "webpage text"
    prompt = (
        f"Extract the cooking recipe from the following {content_type_desc}.\n\n"
        f"Provide:\n"
        f"1. 'name': The recipe title.\n"
        f"2. 'description': Detailed step-by-step preparation and cooking instructions, numbered and formatted with line breaks.\n"
        f"3. 'ingredients': An array of all ingredients. For each ingredient, provide:\n"
        f"   - 'name': Specific ingredient name (e.g. 'flour', 'butter', 'eggs').\n"
        f"   - 'quantity': A numerical float value (e.g. 250, 2, 0.5). If not specified or to taste, use 1 or 0.\n"
        f"   - 'unit': Measurement unit (e.g. 'g', 'ml', 'tbsp', 'tsp', 'pinch', or empty string '' if count/piece).\n\n"
        f"Content to extract:\n{content}"
    )

    system_instruction = (
        "You are an expert culinary assistant. You extract structured cooking recipes accurately. "
        "Always extract accurate numerical quantities and units for each ingredient, and clear step-by-step instructions. "
        "Respond ONLY with the requested JSON object matching the schema."
    )

    schema = {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Recipe title",
            },
            "description": {
                "type": "string",
                "description": "Step-by-step cooking instructions",
            },
            "ingredients": {
                "type": "array",
                "description": "List of recipe ingredients",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "quantity": {"type": "number"},
                        "unit": {"type": "string"},
                    },
                    "required": ["name", "quantity", "unit"],
                },
            },
        },
        "required": ["name", "description", "ingredients"],
    }

    # 1. Primary: Google Gemini Interactions API (/v1beta/interactions)
    interactions_endpoint = (
        f"https://generativelanguage.googleapis.com/v1beta/interactions?key={api_key}"
    )
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key,
    }
    interactions_payload = {
        "model": model,
        "input": prompt,
        "system_instruction": system_instruction,
        "response_format": {
            "type": "text",
            "mime_type": "application/json",
            "schema": schema,
        },
    }

    try:
        resp = requests.post(
            interactions_endpoint,
            headers=headers,
            json=interactions_payload,
            timeout=(5, 30),
        )
    except requests.RequestException as exc:
        raise ExtractionError(f"Error communicating with Gemini API: {exc}")

    if resp.status_code != 200:
        error_details = resp.text
        try:
            err_json = resp.json()
            error_details = err_json.get("error", {}).get("message", resp.text)
        except Exception:
            pass
        logger.error("Gemini API error (%d): %s", resp.status_code, error_details)
        raise ExtractionError(
            f"Gemini API returned error ({resp.status_code}): {error_details}"
        )

    try:
        result = resp.json()
        return _parse_gemini_json_response(result)
    except Exception as exc:
        if isinstance(exc, ExtractionError):
            raise
        logger.error("Failed to parse Gemini API response: %s", exc)
        raise ExtractionError("Failed to parse recipe data from Gemini API response.")


def sanitize_recipe_data(raw: dict) -> dict:
    """
    Sanitizes and validates extracted recipe data against database models and rules.
    """
    if not isinstance(raw, dict):
        raise ExtractionError("Invalid recipe data format.")

    name = str(raw.get("name") or "").strip()
    if not name:
        name = "Untitled Recipe"
    name = name[:250]

    # Description (instructions)
    description = raw.get("description")
    if isinstance(description, list):
        # In case instructions came as a list of strings/steps
        desc_lines = []
        for i, step in enumerate(description, 1):
            if isinstance(step, dict):
                text = step.get("text") or step.get("name") or str(step)
            else:
                text = str(step)
            desc_lines.append(f"{i}. {text.strip()}")
        description = "\n\n".join(desc_lines)
    else:
        description = str(description or "").strip()

    if not description:
        description = "No instructions provided."

    # Ingredients
    raw_ingredients = raw.get("ingredients") or []
    if not isinstance(raw_ingredients, list):
        raw_ingredients = []

    ingredients = []
    for ing in raw_ingredients:
        if not isinstance(ing, dict):
            continue

        ing_name = str(ing.get("name") or "").strip()[:250]
        if not ing_name:
            continue

        raw_qty = ing.get("quantity")
        try:
            quantity = float(raw_qty) if raw_qty is not None else 1.0
        except (ValueError, TypeError):
            quantity = 1.0

        if quantity < 0:
            quantity = 0.0

        unit = str(ing.get("unit") or "").strip()[:100]

        ingredients.append(
            {
                "name": ing_name,
                "quantity": quantity,
                "unit": unit,
            }
        )

    return {
        "name": name,
        "description": description,
        "ingredients": ingredients,
    }


def extract_recipe_from_url(url: str) -> dict:
    """
    Main entry point: validates URL, downloads HTML, extracts recipe data,
    calls Gemini API, and returns sanitized structured recipe dictionary.
    """
    validated_url = validate_url(url)
    html = fetch_html(validated_url)
    payload, is_json_ld = extract_recipe_payload(html)
    raw_data = call_gemini_api(payload, is_json_ld)
    return sanitize_recipe_data(raw_data)
