import json

def lambda_handler(event, context):
    return get_hello_message()

def get_hello_message():
    pubObject = object #will need slot from skill
    pub
    session_attributes = {}
    card_title = "Helping Hand Hello"
    speech_output = "Hello, my name is Helping Hand."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, None, should_end_session))

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        "outputSpeech": {
            "type": "PlainText",
            "text": output
        },
        "card": {
            "type": "Simple",
            "title": title,
            "content": output
        },
        "reprompt": {
            "outputSpeech": {
                "type": "PlainText",
                "text": reprompt_text
            }
        },
        "shouldEndSession": should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes,
        "response": speechlet_response
}
