
#!/usr/bin/env python3

### Your external service class
'''
Your external service class can be named anything you want, and the recommended location would be the lib folder.
It would look like this:

External service sample code
Copyright (C) 2023 Universal Devices

MIT License
'''

import json
import requests
import time
#import urllib
from datetime import timedelta, datetime
from TeslaOauth import teslaAccess
from tzlocal import get_localzone
#from udi_interface import logging, Custom
#from oauth import OAuth
try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
    ISY = udi_interface.ISY
except ImportError:
    import logging
    logging.basicConfig(level=30)


#from udi_interface import logging, Custom, OAuth, ISY
#logging = udi_interface.logging
#Custom = udi_interface.Custom
#ISY = udi_interface.ISY



# Implements the API calls to your external service
# It inherits the OAuth class
class teslaPWAccess(teslaAccess):
    yourApiEndpoint = 'https://fleet-api.prd.na.vn.cloud.tesla.com'

    def __init__(self, polyglot, scope):
        super().__init__(polyglot, scope)
        logging.info('OAuth initializing')
        self.poly = polyglot
        self.scope = scope


        logging.info('External service connectivity initialized...')

        time.sleep(1)

        self.OPERATING_MODES = [ "self_consumption", "autonomous"]
        self.EXPORT_RULES = ['battery_ok', 'pv_only', 'never']
        self.HISTORY_TYPES = ['backup', 'charge', 'energy' ]
        self.DAY_HISTORY = ['today', 'yesterday']
        #self.TOU_MODES = ["economics", "balanced"]
        self.daysConsumption = {}
        self.tokeninfo = {}
        self.touScheduleList = []
        self.connectionEstablished = False
        self.cloudAccess =  self.connectionEstablished
        self.products = {}
        self.history_data = {}
        self.previous_date_str = '' # no previous data stored
        self.date_changed = True
        self.t_now_date = ''
        self.t_now_time = ''
        self.tz_offset = ''
        self.tz_str = ''
        self.t_yesterday_date = ''
        self.update_date_time()
        self.site_info = {}
        self.site_live_info = {}

        #while not self.handleCustomParamsDone:
        #    logging.debug('Waiting for customParams to complete - getAccessToken')
        #    time.sleep(0.2)
        # self.getAccessToken()
    '''
    # The OAuth class needs to be hooked to these 3 handlers
    def customDataHandler(self, data):
        logging.debug('customDataHandler called')
        #while not self.handleCustomParamsDone:
        #    logging.debug('Waiting for customDataHandler to complete')
        #    time.sleep(1)
        super().customDataHandler(data)
        self.customDataHandlerDone = True
        logging.debug('customDataHandler Finished')

    def customNsHandler(self, key, data):
        logging.debug('customNsHandler called')
        #while not self.customParamsDone():
        #    logging.debug('Waiting for customNsHandler to complete')
        #    time.sleep(1)
        #self.updateOauthConfig()
        super().customNsHandler(key, data)
        self.customNsHandlerDone = True
        logging.debug('customNsHandler Finished')

    def oauthHandler(self, token):
        logging.debug('oauthHandler called')
        while not self.customNsDone():
            logging.debug('Waiting for initilization to complete before oAuth')
            time.sleep(5)
        #logging.debug('oauth Parameters: {}'.format(self.getOauthSettings()))
        super().oauthHandler(token)
        #self.customOauthHandlerDone = True
        #while not self.authendication_done :
        try:
            accessToken = self.getAccessToken()
            logging.debug('oauthHandler {} '.format(accessToken))
            self.authendication_done = True
        except ValueError as err:
            logging.error(' No access token exist - try again : {}'.format(err))
            time.sleep(1)
            self.authendication_done = False

        logging.debug('oauthHandler Finished')

    def customNsDone(self):
        return(self.customNsHandlerDone)
    
    def customDateDone(self):
        return(self.customDataHandlerDone )


    #def customOauthDone(self):
    #    return(self.customOauthHandlerDone )
    # Your service may need to access custom params as well...


    
    def cloud_access(self):
        return(self.cloud_access_enabled)
    
    
    


                
    def cloud_initialilze(self, region):
        #self.customParameters.load(userParams)
        #logging.debug('customParamsHandler called {}'.format(userParams))

        oauthSettingsUpdate = {}
        #oauthSettingsUpdate['parameters'] = {}
        oauthSettingsUpdate['token_parameters'] = {}
        # Example for a boolean field

        logging.debug('region {}'.format(self.region))
        oauthSettingsUpdate['scope'] = self.scope 
        oauthSettingsUpdate['auth_endpoint'] = 'https://auth.tesla.com/oauth2/v3/authorize'
        oauthSettingsUpdate['token_endpoint'] = 'https://auth.tesla.com/oauth2/v3/token'
        #oauthSettingsUpdate['redirect_uri'] = 'https://my.isy.io/api/cloudlink/redirect'
        #oauthSettingsUpdate['cloudlink'] = True
        oauthSettingsUpdate['addRedirect'] = True
        #oauthSettingsUpdate['state'] = self.state
        if region.upper() == 'NA':
            endpoint = self.EndpointNA
        elif region.upper() == 'EU':
            endpoint = self.EndpointEU
        elif region.upper() == 'CN':
            endpoint = self.EndpointCN
        else:
            logging.error('Unknow region specified {}'.format(self.region))
            return
           
        self.yourApiEndpoint = endpoint+self.api 
        oauthSettingsUpdate['token_parameters']['audience'] = endpoint
        self.updateOauthSettings(oauthSettingsUpdate)
        time.sleep(0.1)
        logging.debug('getOauthSettings: {}'.format(self.getOauthSettings()))
        #logging.debug('Updated oAuth config 2: {}'.format(temp))
        
        #self.handleCustomParamsDone = True
        #self.poly.Notices.clear()
    
        '''
    def add_to_parameters(self,  key, value):
        #add_to_parameters
        self.customParameters[key] = value

    def check_parameters(self, key, value):
        #check_parameters
        if key in self.customParameters:
            return(self.customParameters[key]  == value)
        else:
            return(False)
        '''

    def getAccessToken(self):
        # Make sure we have received tokens before attempting to renew
        logging.debug('self.getAccessToken: {}'.format(self._oauthTokens))
        if self._oauthTokens is not None and self._oauthTokens.get('refresh_token'):
            expiry = self._oauthTokens.get('expiry')

            # If expired or expiring in less than 60 seconds, refresh
            if ((expiry is None or datetime.fromisoformat(expiry) - timedelta(seconds=60) < datetime.now())):

                logging.info(f"Access tokens: Token is expired since { expiry }. Initiating refresh.")
                self._oAuthTokensRefresh()
            else:
                logging.info(f"Access tokens: Token is still valid until { expiry }, no need to refresh")

            return self._oauthTokens.get('access_token')
        else:
            raise ValueError('Access token is not available')


    
    def _oAuthTokensRefresh(self):
        logging.debug(f"Refresh token before: { self._oauthTokens }")
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self._oauthTokens['refresh_token'],
            'client_id': self._oauthConfig['client_id'],
            'client_secret': self._oauthConfig['client_secret']
        }

        if self._oauthConfig['addRedirect']:
            data['redirect_uri'] = 'https://my.isy.io/api/cloudlink/redirect'

        if self._oauthConfig['scope']:
            data['scope'] = self._oauthConfig['scope']

        if self._oauthConfig['token_parameters'] and isinstance(self._oauthConfig['token_parameters'], dict):
            for key, value in self._oauthConfig['token_parameters'].items():
                data[key] = value

        logging.debug(f"Token refresh body { json.dumps(data) }")

        try:
            response = requests.post(self._oauthConfig['token_endpoint'], data=data)
            response.raise_for_status()
            token = response.json()
            logging.info('Refreshing oAuth tokens successfully')
            logging.debug(f"Token refresh result [{ type(token) }]: { token }")
            self._setExpiry(token)
            self._oauthTokens.load(token)
            self.authendication_done = True
            self.poly.Notices.clear()

        except requests.exceptions.HTTPError as error:
            logging.warning(f"Failed to refresh oAuth token: { error } - try Authenticating again")
            self.poly.Notices['auth'] = 'Please initiate authentication - press Authenticate button'
            raise ValueError('Access token is not available')

            # NOTE: If refresh tokens fails, we keep the existing tokens available.
                
    
    def try_authendication(self):
        if (self._oauthTokens):  # has been authenticated before 
            try:
                accessToken = self.getAccessToken()
                self.poly.Notices.clear()
                logging.debug('access token (try auth {})'.format(self._oauthTokens))
                return(self._oauthTokens.get('expiry') != None)
            except ValueError as err:
                logging.warning('Access token is not yet available. Please authenticate.')
                self.poly.Notices['auth'] = 'Please initiate authentication  - press authenticate'
                logging.debug('try_authendication oauth error: {}'.format(err))
                return (False)
        else:
            self.poly.Notices['auth'] = 'Please initiate authentication - press authenticate'
            return (False)
        

    def authendicated(self):
        logging.debug('authendicated : {} {}'.format(self._oauthTokens.get('expiry') != None, self._oauthTokens))
        return(self._oauthTokens.get('expiry') != None)
 
    # Call your external service API
    def _callApi(self, method='GET', url=None, body=''):
        # When calling an API, get the access token (it will be refreshed if necessary)
        try:
            accessToken = self.getAccessToken()
            self.poly.Notices.clear()
        except ValueError as err:
            logging.warning('Access token is not yet available. Please authenticate.')
            self.poly.Notices['auth'] = 'Please initiate authentication'
            logging.debug('_callAPI oauth error: {}'.format(err))
            return
        if accessToken is None:
            logging.error('Access token is not available')
            return None

        if url is None:
            logging.error('url is required')
            return None

        completeUrl = self.yourApiEndpoint + url

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer { accessToken }'
            
        }

        if method in [ 'PATCH', 'POST'] and body is None:
            logging.error(f"body is required when using { method } { completeUrl }")
        logging.debug(' call info url={}, header {}, body ={}'.format(completeUrl, headers, body))

        try:
            if method == 'GET':
                response = requests.get(completeUrl, headers=headers, json=body)
            elif method == 'DELETE':
                response = requests.delete(completeUrl, headers=headers)
            elif method == 'PATCH':
                response = requests.patch(completeUrl, headers=headers, json=body)
            elif method == 'POST':
                response = requests.post(completeUrl, headers=headers, json=body)
            elif method == 'PUT':
                response = requests.put(completeUrl, headers=headers)

            response.raise_for_status()
            try:
                return response.json()
            except requests.exceptions.JSONDecodeError:
                return response.text

        except requests.exceptions.HTTPError as error:
            logging.error(f"Call { method } { completeUrl } failed: { error }")
            return None
    '''

    # Then implement your service specific APIs
    ########################################
    ############################################
   
    def tesla_get_products(self):
        power_walls= {}
        logging.debug('tesla_get_products ')
        temp = self._callApi('GET','/products' )
        logging.debug('products: {} '.format(temp))
        if 'response' in temp:
            for indx in range(0,len(temp['response'])):
                site = temp['response'][indx]
                if 'energy_site_id' in site:
                    power_walls[str(site['energy_site_id' ])] = site
        return(power_walls)
    
    def tesla_get_live_status(self, site_id):
        logging.debug('tesla_get_live_status ')
        temp = self._callApi('GET','/energy_sites/'+site_id +'/live_status' )
        logging.debug('live_status: {} '.format(temp))
        if 'response' in temp:
            self.site_live_info[site_id] = temp['response']
            return(self.site_live_info[site_id])

    def tesla_get_site_info(self, site_id):
        logging.debug('tesla_get_site_info ')
        temp = self._callApi('GET','/energy_sites/'+site_id +'/site_info' )
        logging.debug('site_info: {} '.format(temp))   
        if 'response' in temp:
            self.site_info[site_id] = temp['response']
            return(self.site_info)

    def tesla_set_backup_percent(self, site_id, reserve_pct):
        logging.debug('tesla_set_backup_percent : {}'.format(reserve_pct))
        reserve = int(reserve_pct)
        body = {'backup_reserve_percent': reserve}
        temp = self._callApi('POST','/energy_sites/'+site_id +'/backup', body )
        logging.debug('backup_percent: {} '.format(temp))   



    def tesla_set_off_grid_vehicle_charging(self, site_id, reserve_pct ):
        logging.debug('tesla_set_off_grid_vehicle_charging : {}'.format(reserve_pct))
        reserve = int(reserve_pct)
        body = {'off_grid_vehicle_charging_reserve_percent': reserve}
        temp = self._callApi('POST','/energy_sites/'+site_id +'/off_grid_vehicle_charging_reserve', body )
        logging.debug('off_grid_vehicle_charging: {} '.format(temp))   

    def tesla_set_grid_import_export(self, site_id, solar_charge, pref_export):
        logging.debug('tesla_set_grid_import_export : {} {}'.format(solar_charge, pref_export))
        if pref_export in self.EXPORT_RULES:
            body = {'disallow_charge_from_grid_with_solar_installed' : solar_charge,
                    'customer_preferred_export_rule': pref_export}
            temp = self._callApi('POST','/energy_sites/'+site_id +'/grid_import_export', body )
            logging.debug('operation: {} '.format(temp))               


    def tesla_set_operation(self, site_id, mode):
        logging.debug('tesla_set_operation : {}'.format(mode))
        if mode in self.OPERATING_MODES:
            body = {'default_real_mode' : mode}
            temp = self._callApi('POST','/energy_sites/'+site_id +'/operation', body )
            logging.debug('operation: {} '.format(temp))               


    def tesla_set_storm_mode(self, site_id, mode):
        logging.debug('tesla_set_storm_mode : {}'.format(mode))
        body = {'enabled' : mode}
        temp = self._callApi('POST','/energy_sites/'+site_id +'/storm_mode', body )
        logging.debug('storm_mode: {} '.format(temp))               

    def update_date_time(self):
        t_now = datetime.now(get_localzone())
        today_date_str = t_now.strftime('%Y-%m-%d')
        self.date_changed = (today_date_str != self.previous_date_str)
        self.previous_date_str = today_date_str
        self.t_now_date = today_date_str
        self.t_now_time = t_now.strftime('T%H:%M:%S')
        tz_offset = t_now.strftime('%z')   
        self.tz_offset = tz_offset[0:3]+':'+tz_offset[-2:]
        self.tz_str = t_now.tzname()
        t_yesterday = t_now - timedelta(days = 1)
        self.t_yesterday_date = t_yesterday.strftime('%Y-%m-%d')


        #t_now = datetime.now(get_localzone())
        #t_yesterday = t_now - timedelta(days = 1)
        #self.yesterday_date = t_yesterday.strftime('%Y-%m-%d')
        #self.today_date = self.t_now.strftime('%Y-%m-%d')


    def tesla_get_today_history(self, site_id, type):
        logging.debug('tesla_get_today_history : {}'.format(type))
        if type in self.HISTORY_TYPES:
            #t_now = datetime.now(get_localzone())
            #self.t_now_date = t_now.strftime('%Y-%m-%d')
            #self.t_now_time = t_now.strftime('T%H:%M:%S')
            #tz_offset = t_now.strftime('%z')   
            #self.tz_offset = tz_offset[0:3]+':'+tz_offset[-2:]
            #tz_str = t_now.tzname()
            t_start_str = self.t_now_date+'T00:00:00'+self.tz_offset
            t_end_str = self.t_now_date+self.t_now_time+self.tz_offset
            params = {
                    'kind'          : type,
                    'start_date'    : t_start_str,
                    'end_date'      : t_end_str,
                    'period'        : 'day',
                    'time_zone'     : self.tz_str
                    #'time_zone'     : 'America/Los_Angeles'
                    }
            logging.debug('body = {}'.format(params))
            hist_data = self._callApi('GET','/energy_sites/'+site_id +'/calendar_history?'+'kind='+str(type)+'&start_date='+t_start_str+'&end_date='+t_end_str+'&period=day'+'&time_zone='+self.tz_str  )
            #temp = self._callApi('GET','/energy_sites/'+site_id +'/calendar_history?'+ urllib.parse.urlencode(params) )
            logging.debug('result ({}) = {}'.format(type, hist_data))
            if hist_data:
                if 'response' in hist_data:
                    self.process_history_data(site_id, type, hist_data['response'])
                else:
                    logging.info ('No data obtained')

    def tesla_get_yesterday_history(self, site_id, type):
        logging.debug('tesla_get_yesterday_history : {}'.format(type))
        if type in self.HISTORY_TYPES:
            #self.prepare_date_time()
            #t_now = datetime.now(get_localzone())
            #t_yesterday = t_now - timedelta(days = 1)
            #t_yesterday_date = t_yesterday.strftime('%Y-%m-%d')
            #t_now_time = t_yesterday.strftime('T%H:%M:%S%z')
            #tz_offset = t_now.strftime('%z')   
            #tz_offset = tz_offset[0:3]+':'+tz_offset[-2:]
            #tz_str = t_now.tzname()
            t_start_str = self.t_yesterday_date+'T00:00:00'+self.tz_offset
            t_end_str = self.t_yesterday_date+'T23:59:59'+self.tz_offset
            params = {
                    'kind'          : type,
                    'start_date'    : t_start_str,
                    'end_date'      : t_end_str,
                    'period'        : 'day',
                    'time_zone'     : self.tz_str
                    #'time_zone'     : 'America/Los_Angeles'
                    }
            logging.debug('body = {}'.format(params))
            hist_data = self._callApi('GET','/energy_sites/'+site_id +'/calendar_history?'+'kind='+str(type)+'&start_date='+t_start_str+'&end_date='+t_end_str+'&period=day'+'&time_zone='+self.tz_str  )
            #temp = self._callApi('GET','/energy_sites/'+site_id +'/calendar_history?'+ urllib.parse.urlencode(params) )
            logging.debug('result ({})= {}'.format(type, hist_data))
            if hist_data:
                if 'response' in hist_data:
                    self.process_history_data(site_id, type, hist_data['response'])
                else:
                    logging.info ('No data obtained')


    def tesla_get_2day_history(self, site_id, type):
        logging.debug('tesla_get_2day_history : {}'.format(type))
        if type in self.HISTORY_TYPES:
            #t_now = datetime.now(get_localzone())
            #t_yesterday = t_now - timedelta(days = 1)
            #t_yesterday_date = t_yesterday.strftime('%Y-%m-%d')
            #t_now_date = t_now.strftime('%Y-%m-%d')
            #t_now_time = t_now.strftime('T%H:%M:%S')
            #tz_offset = t_now.strftime('%z')   
            #tz_offset = tz_offset[0:3]+':'+tz_offset[-2:]
            #tz_str = t_now.tzname()
            t_start_str = self.t_yesterday_date+'T00:00:00'+self.tz_offset
            t_end_str = self.t_now_date+self.t_now_time+self.tz_offset
            params = {
                    'kind'          : type,
                    'start_date'    : t_start_str,
                    'end_date'      : t_end_str,
                    'period'        : 'day',
                    'time_zone'     : self.tz_str
                    #'time_zone'     : 'America/Los_Angeles'
                    }
            logging.debug('body = {}'.format(params))
            hist_data = self._callApi('GET','/energy_sites/'+site_id +'/calendar_history?'+'kind='+str(type)+'&start_date='+t_start_str+'&end_date='+t_end_str+'&period=day'+'&time_zone='+self.tz_str  )
            #temp = self._callApi('GET','/energy_sites/'+site_id +'/calendar_history?'+ urllib.parse.urlencode(params) )
            if hist_data:
                if 'response' in hist_data:
                    logging.debug('result ({}) = {}'.format(type, hist_data['response']))
                    self.process_history_data(site_id, type, hist_data['response'])
                else:
                    logging.info ('No data obtained')



    def process_energy_data(self, site_id, hist_data):
        logging.debug('process_energy_data: {}'.format(hist_data))
    
        for indx in range(0,len(hist_data['time_series'])):
            energy_data = hist_data['time_series'][indx]
            time_str = energy_data['timestamp']
            dt_object = datetime.fromisoformat(time_str)
            date_str = dt_object.strftime('%Y-%m-%d')
            if date_str == self.t_now_date:
                date_key = 'today'                
            elif date_str == self.t_yesterday_date:
                date_key = 'yesterday'
            else:
                date_key = 'unknown'
            if date_key != 'unknown':
                self.history_data[site_id]['energy'][date_key] = energy_data

    def process_backup_data(self, site_id, hist_data):
        logging.debug('process_backup_data: {}'.format(hist_data))
        backup_data = hist_data
        total_duration = 0
        date_key = 'unknown' 
        if int(backup_data['events_count']) > 0:
            time_str = backup_data['events'][0]['timestamp'] # all days should be the same
            dt_object = datetime.fromisoformat(time_str)
            date_str = dt_object.strftime('%Y-%m-%d')
            if date_str == self.t_now_date:
                date_key = 'today'                
            elif date_str == self.t_yesterday_date:
                date_key = 'yesterday'
            else:
                date_key = 'unknown'
            for indx in range(0,len(backup_data['events'])):
                event = backup_data['events'][indx]
                total_duration = total_duration + event['duration']
        temp = {}
        temp['total_duration'] = total_duration
        temp['total_events'] = int(backup_data['total_events'])
        if date_key != 'unknown':
            self.history_data[site_id]['backup'][date_key] = temp

        # need to figure put how to deal with dates
            


    def process_charge_data(self, site_id, hist_data):
        logging.debug('process_charge_data: {}'.format(hist_data))
        charge_data = hist_data
        total_duration = 0
        total_events = 0
        total_energy = 0
        date_key = 'unknown' 
        if 'charge_history' in charge_data:
            if len(charge_data['charge_history']) >  0:
                epoch_time = charge_data['charge_history'][0]['charge_start_time']['seconds'] # all days should be the same
                dt_object = datetime.fromtimestamp(epoch_time)
                date_str = dt_object.strftime('%Y-%m-%d')
                if date_str == self.t_now_date:
                    date_key = 'today'                
                elif date_str == self.t_yesterday_date:
                    date_key = 'yesterday'
                else:
                    date_key = 'unknown'
                total_events = len(charge_data['charge_history'])
                for indx in range(0,len(charge_data['charge_history'])):                    
                    event = charge_data['charge_history'][indx]
                    total_duration = total_duration + charge_data['charge_history'][indx]['charge_duration']['seconds']
                    total_energy = total_energy + charge_data['charge_history'][indx]['energy_added_wh']
        temp = {}
        temp['total_duration'] = total_duration
        temp['total_events'] = total_events
        temp['total_energy'] = total_energy
        if date_key != 'unknown':
            self.history_data[site_id]['backup'][date_key] = temp




    def process_history_data(self, site_id, type, hist_data):
        logging.debug('process_history_data - {} {} {}'.format(site_id, type, hist_data))
        self.update_date_time()
        if site_id not in self.history_data:
            self.history_data[site_id] = {}
        if type not in self.history_data[site_id]:
            self.history_data[site_id][type] = {}

        if type == 'energy':
            self.process_energy_data(site_id, hist_data)
        elif type == 'backup':
            self.process_backup_data(site_id, hist_data)
        elif type == 'charge':
            self.process_charge_data(site_id, hist_data)
        else:
            logging.error('Unknown type provided: {}'.format(type))

        logging.debug('history data: {}'.format(self.history_data))
        



    def teslaUpdateCloudData(self, site_id, mode):
        logging.debug('teslaUpdateCloudData - {} {}'.format( site_id, mode))
        access = False
        self.update_date_time()
        while not self.authendicated():
            self.try_authendication()
            logging.info('Cloud Access not Authenticated yet - press Autenticate button')
            time.sleep(5)
        
        if mode == 'critical':
            temp =self.tesla_get_live_status(site_id)
            self.tesla_get_today_history(site_id, 'energy')
            if temp != None:
                self.site_live_info[site_id] = temp
                access = True
            else:
                access = False
        elif mode == 'all':
            access = False
            temp =self.tesla_get_live_status(site_id)
            if temp != None:
                self.site_live_info[site_id]  = temp
                access = True
            logging.debug('sitelive : {}'.format(self.site_live_info))
            temp = self.tesla_get_site_info(site_id)
            if temp != None:
                self.site_info = temp
                access = True
            logging.debug('site info: {}'.format(self.site_info ))        
            logging.debug('self.site_info {}'.format(self.site_info))    
            
            self.tesla_get_today_history(site_id, 'energy')
            self.tesla_get_today_history(site_id, 'backup')
            self.tesla_get_today_history(site_id, 'charge')
            if self.date_changed:
                self.tesla_get_yesterday_history(site_id, 'energy')
                self.tesla_get_yesterday_history(site_id, 'backup')
                self.tesla_get_yesterday_history(site_id, 'charge')
            logging.debug('history_data : {}'.format(self.history_data))
        return(access)


    def supportedOperatingModes(self):
        return( self.OPERATING_MODES )
 

    def isConnectedToPW(self):
        return( self.authendicated())

 
   
    def teslaSolarInstalled(self, site_id):
        return(self.site_info[site_id]['components']['solar'])

    def tesla_get_pw_name(self, site_id):
        return(self.site_info[site_id]['site_name'])

    def teslaExtractOperationMode(self, site_id):
        return(self.site_info[site_id]['default_real_mode'])

    def teslaExtractStormMode(self, site_id):
        return(self.site_live_info[site_id]['storm_mode_active'])

    def teslaExtractBackupPercent(self, site_id):
        logging.debug('teslaExtractBackupPercent : {} {}'.format(site_id, self.site_info))
        return(self.site_info[site_id]['backup_reserve_percent'])
    
    def tesla_total_battery(self, site_id):
        return(self.site_live_info[site_id][site_id]['total_pack_energy'])
        
    def tesla_remaining_battery (self, site_id):
        return(self.site_live_info[site_id]['energy_left'])
    
    def tesla_island_staus(self, site_id):
        return(self.site_live_info[site_id]['island_status'])
    
    def tesla_grid_staus(self, site_id):
        return(self.site_live_info[site_id]['grid_status'])
    
    def tesla_grid_service_active(self, site_id):
        return(self.site_live_info[site_id]['grid_services_active'])

    def tesla_grid_power(self, site_id):
        return(self.site_live_info[site_id]['grid_power'])
    
    def tesla_generator_power(self, site_id):
        return(self.site_live_info[site_id]['generator_power'])
    
    def tesla_load_power(self, site_id):
        return(self.site_live_info[site_id]['load_power'])
    
    def tesla_battery_power(self, site_id):
        return(self.site_live_info[site_id]['battery_power'])
    
    def tesla_solar_power(self, site_id):
        return(self.site_live_info[site_id]['solar_power'])

    def teslaExtractTouMode(self, site_id):
        return(self.site_info[site_id]['components']['tou_settings']['optimization_strategy'])

    def teslaExtractTouScheduleList(self, site_id):        
        self.touScheduleList = self.site_live_info[site_id]['components']['tou_settings']['schedule']
        return( self.touScheduleList )

    def teslaExtractChargeLevel(self, site_id):
        return(round(self.site_live_info[site_id]['percentage_charged'],2))
        
    #def teslaExtractBackoffLevel(self, site_id):
    #    return(round(self.site_info[site_id]['backup_reserve_percent'],1))

    def teslaExtractGridStatus(self, site_id): 
        return(self.site_live_info[site_id]['island_status'])
    
    def teslaExtractLoad(self, site_id): 
        return(self.site_live_info[site_id]['load_power'])

    def teslaExtractSolarSupply(self, site_id):
        return(self.site_live_info[site_id]['solar_power'])

    def teslaExtractBatterySupply(self, site_id):     
        return(self.site_live_info[site_id]['battery_power'])

    def teslaExtractGridSupply(self, site_id):     
        return(self.site_live_info[site_id]['grid_power'])

    def teslaExtractEnergyRemaining(self, site_id): 
        return(self.site_live_info[site_id]['energy_left'])

    def teslaExtractGeneratorSupply (self, site_id):
        return(self.site_live_info[site_id]['generator_power'])

    def teslaExtractGridServiceActive(self, site_id):
        if self.site_live_info[site_id]['grid_services_active']:
            return(1)
        else:
            return(0)

    '''

    
    		*'solar_energy_exported': 22458, 
			'generator_energy_exported': 0, 
			*'grid_energy_imported': 23080, 
			'grid_services_energy_imported': 7.25, 
			'grid_services_energy_exported': 11.8125, 
			*'grid_energy_exported_from_solar': 15831, 
			*'grid_energy_exported_from_generator': 0, 
			*'grid_energy_exported_from_battery': 77, 
			
			'battery_energy_exported': 10638, 
			'battery_energy_imported_from_grid': 15837,
			'battery_energy_imported_from_solar': 71, 
			'battery_energy_imported_from_generator': 0, 
			energy flow
			'consumer_energy_imported_from_grid': 7243, 
			'consumer_energy_imported_from_solar': 6556, 
			'consumer_energy_imported_from_battery': 10561, 
			'consumer_energy_imported_from_generator': 0}]}}
    '''
    def tesla_grid_energy_import(self, site_id, day):
        if day in self.DAY_HISTORY:
            return(self.history_data[site_id]['energy'][day]['grid_energy_imported'])
        
    def tesla_grid_energy_export(self, site_id, day):    
        if day in self.DAY_HISTORY:
            return(self.history_data[site_id]['energy'][day]['grid_energy_exported_from_solar'] + self.history_data[site_id]['energy'][day]['grid_energy_exported_from_generator'] + self.history_data[site_id]['energy'][day]['grid_energy_exported_from_battery'])

    def tesla_solar_to_grid_energy(self, site_id, day): 
        if day in self.DAY_HISTORY:
            return(self.history_data[site_id]['energy'][day]['grid_energy_exported_from_solar'])

    def tesla_solar_energy_exported(self, site_id, day):
        if day in self.DAY_HISTORY:
            return(self.history_data[site_id]['energy'][day]['solar_energy_exported'])

    def tesla_home_energy_total(self, site_id, day):    
        if day in self.DAY_HISTORY:
            return(self.history_data[site_id]['energy'][day]['consumer_energy_imported_from_grid'] + self.history_data[site_id]['energy'][day]['consumer_energy_imported_from_solar'] + self.history_data[site_id]['energy'][day]['consumer_energy_imported_from_battery'] + self.history_data[site_id]['energy'][day]['consumer_energy_imported_from_generator'] )


    def  tesla_home_energy_solar(self, site_id, day):   
        if day in self.DAY_HISTORY:
            return(self.history_data[site_id]['energy'][day]['consumer_energy_imported_from_solar'])
        
    def  tesla_home_energy_battery(self, site_id, day):   
        if day in self.DAY_HISTORY:
            return(self.history_data[site_id]['energy'][day]['consumer_energy_imported_from_battery'])   
        
    def  tesla_home_energy_grid(self, site_id, day):   
        if day in self.DAY_HISTORY:
            return(self.history_data[site_id]['energy'][day]['consumer_energy_imported_from_grid'])          

    def  tesla_home_energy_generator(self, site_id, day):   
        if day in self.DAY_HISTORY:
            return(self.history_data[site_id]['energy'][day]['consumer_energy_imported_from_generator'])            


    def tesla_battery_energy_import(self, site_id, day):        
        if day in self.DAY_HISTORY:
            return(self.history_data[site_id]['energy'][day]['battery_energy_imported_from_grid'] + self.history_data[site_id]['energy'][day]['battery_energy_imported_from_solar'] + self.history_data[site_id]['energy'][day]['battery_energy_imported_from_generator']  )

    def tesla_battery_energy_export(self, site_id, day):
        if day in self.DAY_HISTORY:
            return(self.history_data[site_id]['energy'][day]['battery_energy_exported'])
        
    def tesla_grid_service_export(self, site_id, day):
        if day in self.DAY_HISTORY:
            return(self.history_data[site_id]['energy'][day]['grid_services_energy_exported'])   

    def tesla_grid_service_import(self, site_id, day):
        if day in self.DAY_HISTORY:
            return(self.history_data[site_id]['energy'][day]['grid_services_energy_imported'])   
    '''
    def teslaExtractDaysSolar(self, site_id):
        return(self.history_data[site_id]['energy']['today']['solar_energy_exported'])
        #return(self.daysConsmuption['solar_power'])
    
    def teslaExtractDaysConsumption(self, site_id):
        return(self.history_data[site_id]['energy']['today']['solar_energy_exported'])
        #return(self.daysConsumption['consumed_power'])

    def teslaExtractDaysGeneration(self, site_id):
        return(self.history_data[site_id]['energy']['today']['solar_energy_exported'])
        #return(self.daysConsumption['net_generation'])

    def teslaExtractDaysBattery(self, site_id): 
        return(self.history_data[site_id]['energy']['today']['solar_energy_exported'])
        #return(self.daysConsumption['battery_power'])

    def teslaExtractDaysGrid(self, site_id):         
        return(self.history_data[site_id]['energy']['today']['solar_energy_exported'])
        #return(self.daysConsumption['net_power'])

    def teslaExtractDaysGridServicesUse(self, site_id):
        return(self.history_data[site_id]['energy']['today']['solar_energy_exported'])
        #return(self.daysConsumption['grid_services_power'])

    def teslaExtractDaysGeneratorUse(self, site_id):
        return(self.history_data[site_id]['energy']['today']['solar_energy_exported'])
        #return(self.daysConsumption['generator_power'])  

    def teslaExtractYesteraySolar(self, site_id):
        return(self.daysConsumption['yesterday_solar_power'])
    
    def teslaExtractYesterdayConsumption(self, site_id):     
        return(self.daysConsumption['yesterday_consumed_power'])

    def teslaExtractYesterdayGeneraton(self, site_id):         
        return(self.daysConsumption['net_generation'])

    def teslaExtractYesterdayBattery(self, site_id):         
        return(self.daysConsumption['yesterday_battery_power'])

    def teslaExtractYesterdayGrid(self, site_id):         
        return(self.daysConsumption['yesterday_net_power'])

    def teslaExtractYesterdayGridServiceUse(self, site_id):         
        return(self.daysConsumption['yesterday_grid_services_power'])

    def teslaExtractYesterdayGeneratorUse(self, site_id):         
        return(self.daysConsumption['yesterday_generator_power'])  

    def teslaExtractOperationMode(self, site_id):         
        return(self.site_info['default_real_mode'])

    def teslaExtractConnectedTesla(self, site_id):       
        return(True)

    def teslaExtractRunning(self, site_id):  
        return(True)
    
    #???
    def teslaExtractPowerSupplyMode(self, site_id):  
        return(True)

    def teslaExtractGridServiceActive(self, site_id):
        if self.site_live_info[site_id]['grid_services_active']: 
            return(1)
        else:
            return(0)
    '''