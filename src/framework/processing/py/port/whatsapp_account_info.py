"""
DDP Whatsapp account info module

This module contains functions to handle *.jons files contained within Whatsapp account info
"""

from pathlib import Path
import logging
import zipfile

import pandas as pd

import port.unzipddp as unzipddp
import port.api.props as props
from port.validate import (
    DDPCategory,
    StatusCode,
    ValidateInput,
    Language,
    DDPFiletype,
)

logger = logging.getLogger(__name__)


DDP_CATEGORIES = [
    DDPCategory(
        id="json_html_en",
        ddp_filetype=DDPFiletype.JSON,
        language=Language.EN,
        known_files=[
            "index.html",
            "avatars_information.html",
            "avatars_information.json",
            "registration_information.html",
            "registration_information.json",
            "user_information.html",
            "user_information.json",
            "contacts.html",
            "contacts.json",
            "groups.html",
            "groups.json",
            "account_settings.html",
            "account_settings.json",
            "terms_of_service.html",
            "terms_of_service.json"
         ],
    )
]

STATUS_CODES = [
    StatusCode(id=0, description="Valid DDP", message="Valid DDP"),
    StatusCode(id=1, description="Not a valid DDP", message="Not a valid DDP"),
    StatusCode(id=2, description="Bad zipfile", message="Bad zip"),
]


def validate(zfile: Path) -> ValidateInput:
    """
    Make sure you always set a status code
    """

    validate = ValidateInput(STATUS_CODES, DDP_CATEGORIES)

    try:
        paths = []
        with zipfile.ZipFile(zfile, "r") as zf:
            for f in zf.namelist():
                p = Path(f)
                if p.suffix in (".html", ".json"):
                    logger.debug("Found: %s in zip", p.name)
                    paths.append(p.name)

        if validate.infer_ddp_category(paths):
            validate.set_status_code_by_id(0)
        else:
            validate.set_status_code_by_id(1)
    except zipfile.BadZipFile:
        validate.set_status_code_by_id(1)

    return validate



def ncontacts_ngroups_device_to_df(whatsapp_account_info_zip: str) -> pd.DataFrame:
    out = pd.DataFrame()
    datapoints = []

    # Extract number of contacts
    b = unzipddp.extract_file_from_zip(whatsapp_account_info_zip, "contacts.json")
    d = unzipddp.read_json_from_bytes(b)
    try:
        items = d["wa_contacts"]
        datapoints.append(("Number of contacts", len(items)))
    except Exception as e:
        logger.error("Exception caught: %s", e)

    # Extract number of groups
    b = unzipddp.extract_file_from_zip(whatsapp_account_info_zip, "groups.json")
    d = unzipddp.read_json_from_bytes(b)
    try:
        items = d["wa_groups"]
        datapoints.append(("Number of groups", len(items)))
    except Exception as e:
        logger.error("Exception caught: %s", e)

    # Extract platform 
    b = unzipddp.extract_file_from_zip(whatsapp_account_info_zip, "registration_information.json")
    d = unzipddp.read_json_from_bytes(b)
    print(d)
    try:
        platform = d["wa_registration_info"].get("platform", "").lower()
        description = "Platform name"
        print(platform)
        if "iphone" in platform:
            datapoints.append((description, "iPhone"))
        elif "android" in platform:
            datapoints.append((description, "Android"))
        else:
            pass # dont append datapoint

    except Exception as e:
        logger.error("Exception caught: %s", e)

    if len(datapoints) > 0:
        out = pd.DataFrame(datapoints, columns=["Description", "Value"])

    return out


def extract(account_info_zip: str, _) -> list[props.PropsUIPromptConsentFormTable]:
    """
    Main data extraction function
    Assemble all extraction logic here
    """
    tables_to_render = []

    # Extract comments
    df = ncontacts_ngroups_device_to_df(account_info_zip)
    if not df.empty:
        table_title = props.Translatable({
            "en": "Whatsapp Account information",
            "nl": "Whatsapp Account information",
        })
        table_description = props.Translatable({
            "en": "In this table you can see: the number of groups you are a part of, the number of contacts you have, and you use WhatsApp on", 
            "nl": "In this table you can see: the number of groups you are a part of, the number of contacts you have, and you use WhatsApp on", 
        })
        table = props.PropsUIPromptConsentFormTable("all", table_title, df, table_description)
        tables_to_render.append(table)

    return tables_to_render
