# -*- coding: utf-8 -*-
import requests
import json
import boto3
from lxml.html import parse

CardTitlePrefix = "Greeting"

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    """
    Build a speechlet JSON representation of the title, output text, 
    reprompt text & end of session
    """
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': CardTitlePrefix + " - " + title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }
    
def build_response(session_attributes, speechlet_response):
    """
    Build the full response JSON from the speechlet response
    """
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }

def get_welcome_response():
    welcome_response= "Welcome to the L.A. Board of Supervisors Skill. You can say, give me recent motions or give me the latest agenda."
    print(welcome_response);

    session_attributes = {}
    card_title = "Hello"
    speech_output = welcome_response;
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "I'm sorry - I didn't understand. You should say give me latest motions."
    should_end_session = True
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))

def replace_with_longform_name(name):

    if name == "LASD":
        longformName = "Los Angeles County Sheriff's Department"
    elif name == "DMH":
        longformName = "Department of Mental Health"
    else:
        longformName = name;

    return longformName;


def get_next_motions_response(session):
    
    print("Initial session attributes are "+str(session['attributes']));

    if "result_number" not in session['attributes']:
        print("Second session attributes are "+str(session['attributes']));
        session['attributes']['result_number'] = 1;
        print("Value is "+str(session['attributes']['result_number']));
        print("Final session attributes are "+str(session['attributes']))

    result_number = session['attributes']['result_number'];
    host = "http://api.lacounty.gov";

    url = host + "/searchAPIWeb/searchapi?type=bcsearch&database=OMD&" \
                 "SearchTerm=1&title=1&content=1&PStart=" + str(result_number) +"&PEnd=" + str(result_number) +"&_=1509121047612"

    response = requests.get(url);
    #print(response.text);
    data = json.loads(response.text)

    alexaResponse = "";
    if(result_number == 1):
        alexaResponse = "Here is the latest correspondence before the L.A. board (both upcoming and past): "

    alexaResponse += str(result_number)+": From the "+replace_with_longform_name(data["results"][0]["department"])+ ", "
    alexaResponse += "on "+data["results"][0]["date"]+", "
    alexaResponse += data["results"][0]["title"]+"... "
    
    alexaResponse += "You can say text me link or next item"
    
    session['attributes']['result_number'] = result_number + 1;
    session['attributes']['result_url'] = data["results"][0]["url"];
    
    #text_url_to_number(session);
    reprompt_text = "I'm sorry - I didn't understand. You should say text me link or next item"
    
    card_title = "LA Board Latest Motions Message";
    greeting_string = alexaResponse;
    return build_response(session['attributes'], build_speechlet_response(card_title, greeting_string, reprompt_text, False))
    
def get_next_agenda_response(session):
    
    print("Initial session attributes are "+str(session['attributes']));
    
    host = "http://bos.lacounty.gov/Board-Meeting/Board-Agendas";
    url = host;
    page = parse(url)
    nodes = page.xpath("//div[a[text()='View Agenda']]");
    latest_agenda_node = nodes[0];
    headline = latest_agenda_node.find("ul").xpath("string()").strip();
    
    print(headline);
    agenda_url = latest_agenda_node.find("a[@href]").attrib['href'];
    print("http://bos.lacounty.gov"+agenda_url)
    
    agenda_heading = headline;
    #session['attributes']['result_url']
    session['attributes']['result_url'] = "http://bos.lacounty.gov"+agenda_url;
    card_title = "Agenda";
    greeting_string = "I have a link for the "+agenda_heading+". Say text me and I'll send it to you.";
    reprompt = "Say text me to receive a link to the agenda."

    return build_response(session['attributes'], build_speechlet_response(card_title, greeting_string, reprompt, False))
    
    
def text_url_to_number(session, intent):
    
    if "phone_number" not in session['attributes'] and "value" not in intent['slots']['phoneNumber']:
        greeting_string = "Say your nine digit phone number, including the area code";
        card_title = "What's your phone number?";
        reprompt_text = "I didn't understand. Please say your nine digit mobile phone number."
        return build_response(session['attributes'], build_speechlet_response(card_title, greeting_string, reprompt_text, False))
    else:
        number = intent['slots']['phoneNumber']['value'];
        if "result_url" not in session['attributes']:
            session['attributes']['result_url'] = 'http://portal.lacounty.gov/wps/portal/omd';
            
        url = session['attributes']['result_url'];
        session['attributes']['phone_number'] = number;
    
        sns_client = boto3.client('sns')
        response = sns_client.publish(
            PhoneNumber='1'+str(number), 
            Message="Thank you for using the LA Board of Supervisors Skill. Here's your URL: "+url
        )
        greeting_string = "Sent text message to "+ " ".join(number);
        card_title = "Sent motion URL via text message";
        reprompt_text = "I didn't understand. Please say your nine digit mobile phone number."
        return build_response(session['attributes'], build_speechlet_response(card_title, greeting_string, reprompt_text, True))

def on_session_started(session_started_request, session):
    """ Called when the session starts """
    
    #session.attributes['result_number'] = 1
    session['attributes'] = {}
    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])

def handle_session_end_request():
    card_title = "County of LA Board of Supervisors Skill- Thanks"
    speech_output = "Thank you for using the County of LA Board of Supervisors Skill. See you next time!"
    should_end_session = True
    return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session));
    
def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they want """
    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()
    
def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """
    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])
          
    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']
    # Dispatch to your skill's intent handlers
    if intent_name == "GetLatestAgendaIntent":
        return get_next_agenda_response(session)
    elif intent_name == "GetLatestMotionsIntent":
        return get_next_motions_response(session)
    elif intent_name == "GetNextMotionIntent":
        return get_next_motions_response(session)
    elif intent_name == "SetPhoneNumberIntent":
        return text_url_to_number(session, intent);
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")

def lambda_handler(event, context):
    print("Test!")
    
    print("event.session.application.applicationId=" +
        event['session']['application']['applicationId'])
        
    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])
    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return handle_session_end_request()
