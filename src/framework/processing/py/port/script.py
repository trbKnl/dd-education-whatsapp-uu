import logging
import json
import io
import pandas as pd

from port.api.commands import (CommandSystemDonate, CommandSystemExit, CommandUIRender)
import port.api.props as props

import port.whatsapp_account_info as whatsapp_account_info
import port.whatsapp as whatsapp


LOG_STREAM = io.StringIO()

logging.basicConfig(
    #stream=LOG_STREAM,
    level=logging.INFO,
    format="%(asctime)s --- %(name)s --- %(levelname)s --- %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z",
)

LOGGER = logging.getLogger("script")


def process(session_id):
    flows = [
        whatsapp_chat_flow,
        whatsapp_account_info_flow,
    ]

    #flows = [ whatsapp_chat_flow ]
    #flows = [ whatsapp_account_info_flow ]

    for flow in flows:
        yield from flow(session_id)

    yield exit(0, "Success")
    yield render_end_page()


##################################################################
# Whatsapp chat

SUBMIT_FILE_HEADER_WHATSAPP = props.Translatable({
    "en": "Select your Whatsapp Group Chat file", 
    "nl": "Select your Whatsapp Group Chat file", 
})

REVIEW_DATA_HEADER_WHATSAPP = props.Translatable({
    "en": "Your Whatsapp Group Chat data", 
    "nl": "Your Whatsapp Group Chat data", 
})

RETRY_HEADER_WHATSAPP = props.Translatable({
    "en": "Try again", 
    "nl": "Probeer opnieuw"
})


def whatsapp_chat_flow(session_id):

    platform_name = "Whatsapp Group Chat"
    list_with_consent_form_tables = []
    selected_username = ""

    while True:
        file_prompt = generate_file_prompt("application/zip")
        file_result = yield render_page(SUBMIT_FILE_HEADER_WHATSAPP, file_prompt)

        if file_result.__type__ == 'PayloadString':
            df = whatsapp.parse_chat(file_result.value)

            # Sad flow
            if df.empty:
                retry_result = yield render_page(RETRY_HEADER_WHATSAPP, retry_confirmation(platform_name))
                if retry_result.__type__ == "PayloadTrue":
                    continue
                else:
                    break

            # Happy flow
            else:

                df = whatsapp.remove_empty_chats(df)
                users = whatsapp.extract_users(df)
                df = whatsapp.keep_users(df, users)

                if len(users) < 3:
                    retry_result = yield render_page(RETRY_HEADER_WHATSAPP, retry_confirmation(platform_name))
                    if retry_result.__type__ == "PayloadTrue":
                        continue
                    else:
                        break

                if selected_username == "":
                    selection = yield prompt_radio_menu(platform_name, users)
                    # If user skips during this process, selectedUsername remains equal to ""
                    if selection.__type__ == "PayloadString":
                        selected_username = selection.value
                    else:
                        break
                    
                    df = whatsapp.anonymize_users(df, users, selected_username)
                    anonymized_users_list = [ f"Member {i + 1}" for i in range(len(users))]
                    for user_name in anonymized_users_list:
                        statistics_table = whatsapp.deelnemer_statistics_to_df(df, user_name)
                        if statistics_table != None:
                            list_with_consent_form_tables.append(statistics_table)

                    break

        # skip file select
        else:
            break

    if len(list_with_consent_form_tables) > 0: 
        prompt = create_consent_form(list_with_consent_form_tables)
        consent_result = yield render_page(REVIEW_DATA_HEADER_WHATSAPP, prompt)

        if consent_result.__type__ == "PayloadJSON":
            yield donate(f"{session_id}-{platform_name}", consent_result.value)

            render_questionnaire_results = yield render_questionnaire_whatsapp_chat()
            if render_questionnaire_results.__type__ == "PayloadJSON":
                yield donate(f"{session_id}-questionnaire-whatsapp-chat", render_questionnaire_results.value)

    return 


##################################################################
# Whatsapp account info


SUBMIT_FILE_HEADER_WHATSAPP_ACCOUNT_INFO = props.Translatable({
    "en": "Select your Whatsapp Account Information file", 
    "nl": "Select your Whatsapp Account Information file", 
})

REVIEW_DATA_HEADER_WHATSAPP_ACCOUNT_INFO = props.Translatable({
    "en": "Your Whatsapp Account data", 
    "nl": "Your Whatsapp Account data data", 
})

RETRY_HEADER_WHATSAPP_ACCOUNT_INFO = props.Translatable({
    "en": "Try again", 
    "nl": "Probeer opnieuw"
})


def whatsapp_account_info_flow(session_id):

    platform_name, extraction_fun, validation_fun = (
        "Whatsapp Account Information", 
        whatsapp_account_info.extract, 
        whatsapp_account_info.validate,
    )
    table_list = None

    # Prompt file extraction loop
    while True:
        file_prompt = generate_file_prompt("application/zip, text/plain, application/json")
        file_result = yield render_page(SUBMIT_FILE_HEADER_WHATSAPP_ACCOUNT_INFO, file_prompt)

        if file_result.__type__ == "PayloadString":
            validation = validation_fun(file_result.value)

            # DDP is recognized: Status code zero
            if validation.status_code.id == 0: 
                LOGGER.info("Payload for %s", platform_name)
                table_list = extraction_fun(file_result.value, validation)
                break

            # DDP is not recognized: Different status code
            if validation.status_code.id != 0: 

                retry_result = yield render_page(RETRY_HEADER_WHATSAPP_ACCOUNT_INFO, retry_confirmation(platform_name))
                if retry_result.__type__ == "PayloadTrue":
                    continue
                else:
                    break
        else:
            break

    # Render data on screen
    if table_list is not None:
        # Check if extract something got extracted
        if len(table_list) == 0:
            table_list.append(create_empty_table(platform_name))
        else:
            # Short Questionnaire
            render_questionnaire_results = yield render_questionnaire_whatsapp_account_info()
            if render_questionnaire_results.__type__ == "PayloadJSON":
                yield donate(f"{session_id}-questionnaire-whatsapp-account-info", render_questionnaire_results.value)

        prompt = create_consent_form(table_list)
        consent_result = yield render_page(REVIEW_DATA_HEADER_WHATSAPP_ACCOUNT_INFO, prompt)

        if consent_result.__type__ == "PayloadJSON":
            yield donate(f"{session_id}-whatsapp-account-info", consent_result.value)



##################################################################

def create_consent_form(table_list: list[props.PropsUIPromptConsentFormTable]) -> props.PropsUIPromptConsentForm:
    """
    Assembles all donated data in consent form to be displayed
    """
    return props.PropsUIPromptConsentForm(table_list, meta_tables=[])


def donate_logs(key):
    log_string = LOG_STREAM.getvalue()  # read the log stream
    if log_string:
        log_data = log_string.split("\n")
    else:
        log_data = ["no logs"]

    return donate(key, json.dumps(log_data))


def donate_status(filename: str, message: str):
    return donate(filename, json.dumps({"status": message}))


def render_end_page():
    page = props.PropsUIPageEnd()
    return CommandUIRender(page)


def render_page(header_text, body):
    header = props.PropsUIHeader(header_text)

    footer = props.PropsUIFooter()
    platform = "ChatGPT"
    page = props.PropsUIPageDonation(platform, header, body, footer)
    return CommandUIRender(page)


def retry_confirmation(platform):
    text = props.Translatable(
        {
            "en": f"Unfortunately, we could not process your {platform} file. If you are sure that you selected the correct file, press Continue. To select a different file, press Try again.",
            "nl": f"Helaas, kunnen we uw {platform} bestand niet verwerken. Weet u zeker dat u het juiste bestand heeft gekozen? Ga dan verder. Probeer opnieuw als u een ander bestand wilt kiezen."
        }
    )
    ok = props.Translatable({"en": "Try again", "nl": "Probeer opnieuw"})
    cancel = props.Translatable({"en": "Continue", "nl": "Verder"})
    return props.PropsUIPromptConfirm(text, ok, cancel)


def generate_file_prompt(extensions):
    description = props.Translatable(
        {
            "en": f"Please follow the download instructions and choose the file that you stored on your device.",
            "nl": f"Volg de download instructies en kies het bestand dat u opgeslagen heeft op uw apparaat."
        }
    )
    return props.PropsUIPromptFileInput(description, extensions)


def donate(key, json_string):
    return CommandSystemDonate(key, json_string)


def exit(code, info):
    return CommandSystemExit(code, info)


def prompt_radio_menu(platform, list_with_users):
    title = props.Translatable({
        "en": f"",
        "nl": f""
    })
    description = props.Translatable({
        "en": f"Please select your username",
        "nl": f"Selecteer uw gebruikersnaam"
    })
    header = props.PropsUIHeader(props.Translatable({
        "en": "Submit Whatsapp groupchat",
        "nl": "Submit Whatsapp groupchat"
    }))

    radio_input = [{"id": index, "value": username} for index, username in enumerate(list_with_users)]
    body = props.PropsUIPromptRadioInput(title, description, radio_input) #pyright: ignore
    footer = props.PropsUIFooter()
    page = props.PropsUIPageDonation(platform, header, body, footer)
    return CommandUIRender(page)


def create_empty_table(platform_name: str) -> props.PropsUIPromptConsentFormTable:
    """
    Show something in case no data was extracted
    """
    title = props.Translatable({
       "en": "Er ging niks mis, maar we konden niks vinden",
       "nl": "Er ging niks mis, maar we konden niks vinden"
    })
    df = pd.DataFrame(["No data found"], columns=["No data found"]) #pyright: ignore
    table = props.PropsUIPromptConsentFormTable(f"{platform_name}_no_data_found", title, df)
    return table


#################################################################################################
# Questionnaire group chat

PURPOSE_GROUP = props.Translatable({
    "en": " What is the purpose of the Whatsapp group you donated data about?",
    "nl": " What is the purpose of the Whatsapp group you donated data about?",
})


def render_questionnaire_whatsapp_chat():
    questions = [
        props.PropsUIQuestionOpen(question=PURPOSE_GROUP, id=1),
    ]
    description = props.Translatable({"en": "", "nl": ""})
    header = props.PropsUIHeader(props.Translatable({"en": "Questionnaire", "nl": "Questionnaire"}))
    body = props.PropsUIPromptQuestionnaire(questions=questions, description=description)
    footer = props.PropsUIFooter()

    page = props.PropsUIPageDonation("questionnaire", header, body, footer)
    return CommandUIRender(page)



#################################################################################################
# Questionnaire account info

NCONTACTS = props.Translatable({
    "en": "Estimate the number Whatsapp contacts in your contact list (please enter a number)",
    "nl": "Estimate the number Whatsapp contacts in your contact list (please enter a number)",
})

NGROUPS = props.Translatable({
    "en": "Estimate the number Whatsapp groups you are in (please enter a number)",
    "nl": "Estimate the number Whatsapp groups you are in (please enter a number)",
})

GENDER = props.Translatable({"en": "What is your gender?", "nl": "What is your gender?"})
GENDER_CHOICES = [
    props.Translatable({"en": "Male", "nl": "Male"}),
    props.Translatable({"en": "Female", "nl": "Female"}),
    props.Translatable({"en": "Other", "nl": "Other"}),
    props.Translatable({"en": "Don't want to say", "nl": "Don't want to say"})
]

def render_questionnaire_whatsapp_account_info():
    questions = [
        props.PropsUIQuestionMultipleChoice(question=GENDER, id=1, choices=GENDER_CHOICES),
        props.PropsUIQuestionOpen(question=NCONTACTS, id=3),
        props.PropsUIQuestionOpen(question=NGROUPS, id=4),
    ]

    description = props.Translatable({
        "en": "Before we show the result of the extraction a few questions", 
        "nl": "Before we show the result of the extraction a few questions", 
    })
    header = props.PropsUIHeader(props.Translatable({"en": "Questionnaire", "nl": "Questionnaire"}))
    body = props.PropsUIPromptQuestionnaire(questions=questions, description=description)
    footer = props.PropsUIFooter()

    page = props.PropsUIPageDonation("questionnaire", header, body, footer)
    return CommandUIRender(page)

