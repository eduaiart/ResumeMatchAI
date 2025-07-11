"""
Google Calendar Service for Fit2Hire
Handles all Google Calendar API interactions for scheduling appointments
"""

import os
import json
import pytz
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from flask import session, url_for, request


class GoogleCalendarService:
    """Service class for Google Calendar API operations"""
    
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/calendar']
        self.client_config = None
        self.setup_client_config()
    
    def setup_client_config(self):
        """Setup OAuth2 client configuration"""
        client_id = os.environ.get('GOOGLE_CLIENT_ID')
        client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            raise ValueError("Google OAuth credentials not found. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables.")
        
        self.client_config = {
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [self.get_redirect_uri()]
            }
        }
    
    def get_redirect_uri(self):
        """Get the OAuth redirect URI based on environment"""
        base_url = os.environ.get('REPLIT_DOMAIN', 'http://localhost:5000')
        if base_url.startswith('https://'):
            return f"{base_url}/oauth2callback"
        else:
            return f"{base_url}/oauth2callback"
    
    def get_auth_url(self):
        """Get the authorization URL for OAuth flow"""
        flow = Flow.from_client_config(
            self.client_config,
            scopes=self.SCOPES,
            redirect_uri=self.get_redirect_uri()
        )
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        session['oauth_state'] = state
        return authorization_url
    
    def handle_oauth_callback(self, authorization_response):
        """Handle OAuth callback and exchange code for tokens"""
        state = session.get('oauth_state')
        
        flow = Flow.from_client_config(
            self.client_config,
            scopes=self.SCOPES,
            state=state,
            redirect_uri=self.get_redirect_uri()
        )
        
        try:
            flow.fetch_token(authorization_response=authorization_response)
            credentials = flow.credentials
            
            # Store credentials in session
            session['google_credentials'] = self._credentials_to_dict(credentials)
            return True
        except Exception as e:
            print(f"OAuth callback error: {e}")
            return False
    
    def get_calendar_service(self):
        """Get authenticated Calendar service"""
        if 'google_credentials' not in session:
            return None
        
        credentials = Credentials(**session['google_credentials'])
        
        # Check if credentials are valid
        if not credentials.valid:
            if credentials.expired and credentials.refresh_token:
                try:
                    credentials.refresh(Request())
                    session['google_credentials'] = self._credentials_to_dict(credentials)
                except Exception as e:
                    print(f"Token refresh error: {e}")
                    return None
            else:
                return None
        
        return build('calendar', 'v3', credentials=credentials)
    
    def create_appointment(self, candidate_name, candidate_email, interviewer_name, interviewer_email, 
                          start_time, end_time, job_title, meeting_type="Interview"):
        """Create a calendar appointment for interview scheduling"""
        service = self.get_calendar_service()
        if not service:
            return None
        
        # Convert to UTC if timezone aware
        if start_time.tzinfo is None:
            start_time = pytz.UTC.localize(start_time)
        if end_time.tzinfo is None:
            end_time = pytz.UTC.localize(end_time)
        
        # Create event
        event = {
            'summary': f"{meeting_type}: {candidate_name} - {job_title}",
            'description': f"""
{meeting_type} scheduled through Fit2Hire

Candidate: {candidate_name} ({candidate_email})
Interviewer: {interviewer_name} ({interviewer_email})
Position: {job_title}

This meeting was automatically scheduled through the Fit2Hire system.
            """.strip(),
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'UTC',
            },
            'attendees': [
                {'email': candidate_email, 'displayName': candidate_name},
                {'email': interviewer_email, 'displayName': interviewer_name}
            ],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},  # 24 hours
                    {'method': 'popup', 'minutes': 30},        # 30 minutes
                ],
            },
            'conferenceData': {
                'createRequest': {
                    'requestId': f"fit2hire-{datetime.now().timestamp()}",
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                }
            }
        }
        
        try:
            created_event = service.events().insert(
                calendarId='primary',
                body=event,
                conferenceDataVersion=1,
                sendUpdates='all'
            ).execute()
            
            return {
                'event_id': created_event['id'],
                'event_link': created_event.get('htmlLink'),
                'meet_link': created_event.get('conferenceData', {}).get('entryPoints', [{}])[0].get('uri'),
                'status': 'created'
            }
        except HttpError as error:
            print(f"Calendar API error: {error}")
            return None
    
    def get_available_slots(self, start_date, end_date, duration_minutes=60):
        """Get available time slots for scheduling"""
        service = self.get_calendar_service()
        if not service:
            return []
        
        try:
            # Get busy times
            body = {
                'timeMin': start_date.isoformat(),
                'timeMax': end_date.isoformat(),
                'items': [{'id': 'primary'}]
            }
            
            events_result = service.freebusy().query(body=body).execute()
            busy_times = events_result['calendars']['primary']['busy']
            
            # Generate available slots (9 AM to 5 PM, weekdays only)
            available_slots = []
            current_date = start_date.date()
            end_date_only = end_date.date()
            
            while current_date <= end_date_only:
                # Skip weekends
                if current_date.weekday() < 5:  # Monday = 0, Friday = 4
                    # Check each hour from 9 AM to 5 PM
                    for hour in range(9, 17):
                        slot_start = datetime.combine(current_date, datetime.min.time().replace(hour=hour))
                        slot_start = pytz.UTC.localize(slot_start)
                        slot_end = slot_start + timedelta(minutes=duration_minutes)
                        
                        # Check if slot conflicts with busy times
                        is_available = True
                        for busy in busy_times:
                            busy_start = datetime.fromisoformat(busy['start'].replace('Z', '+00:00'))
                            busy_end = datetime.fromisoformat(busy['end'].replace('Z', '+00:00'))
                            
                            if (slot_start < busy_end and slot_end > busy_start):
                                is_available = False
                                break
                        
                        if is_available:
                            available_slots.append({
                                'start': slot_start,
                                'end': slot_end,
                                'display': slot_start.strftime('%Y-%m-%d %H:%M UTC')
                            })
                
                current_date += timedelta(days=1)
            
            return available_slots
        except HttpError as error:
            print(f"Calendar API error: {error}")
            return []
    
    def update_appointment(self, event_id, **kwargs):
        """Update an existing appointment"""
        service = self.get_calendar_service()
        if not service:
            return None
        
        try:
            # Get existing event
            event = service.events().get(calendarId='primary', eventId=event_id).execute()
            
            # Update fields
            if 'start_time' in kwargs:
                event['start']['dateTime'] = kwargs['start_time'].isoformat()
            if 'end_time' in kwargs:
                event['end']['dateTime'] = kwargs['end_time'].isoformat()
            if 'summary' in kwargs:
                event['summary'] = kwargs['summary']
            if 'description' in kwargs:
                event['description'] = kwargs['description']
            
            # Update event
            updated_event = service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event,
                sendUpdates='all'
            ).execute()
            
            return {
                'event_id': updated_event['id'],
                'event_link': updated_event.get('htmlLink'),
                'status': 'updated'
            }
        except HttpError as error:
            print(f"Calendar API error: {error}")
            return None
    
    def cancel_appointment(self, event_id):
        """Cancel an appointment"""
        service = self.get_calendar_service()
        if not service:
            return False
        
        try:
            service.events().delete(
                calendarId='primary',
                eventId=event_id,
                sendUpdates='all'
            ).execute()
            return True
        except HttpError as error:
            print(f"Calendar API error: {error}")
            return False
    
    def _credentials_to_dict(self, credentials):
        """Convert credentials to dictionary for session storage"""
        return {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
    
    def is_authenticated(self):
        """Check if user is authenticated with Google Calendar"""
        return 'google_credentials' in session