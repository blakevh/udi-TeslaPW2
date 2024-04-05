#!/usr/bin/env python3

import time

try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=30)

from TeslaInfo import tesla_info
from TeslaPWSetupNode import teslaPWSetupNode
from TeslaPWSolarNode import teslaPWSolarNode
from TeslaPWGenNode import teslaPWGenNode
from TeslaPWHistoryNode import teslaPWHistoryNode


class teslaPWStatusNode(udi_interface.Node):
    from  udiLib import node_queue, wait_for_node_done, mask2key

    def __init__(self, polyglot, primary, address, name, TPW):
        #super(teslaPWStatusNode, self).__init__(polyglot, primary, address, name)
        logging.info('_init_ Tesla Power Wall Status Node')
        self.poly = polyglot
        self.ISYforced = False
        self.TPW = TPW
        self.node_ok = False
        self.address = address
        self.primary = primary
        self.name = name
        self.n_queue = []
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
        self.poly.subscribe(self.poly.START, self.start, address)

        self.poly.ready()
        self.poly.addNode(self)
        self.wait_for_node_done()
        self.node = self.poly.getNode(address)
        #self.TPW = tesla_info(self.my_TeslaPW, self.site_id)
        #self.TPW.tesla_get_site_info(self.site_id)
        #self.TPW.tesla_get_live_status(self.site_id)
        
        #polyglot.subscribe(polyglot.START, self.start, address)
        
    def start(self):   
        logging.debug('Start Tesla Power Wall Status Node')
        #self.TPW = tesla_info(self.my_TeslaPW, self.site_id)
        logging.info('Adding power wall sub-nodes')

        sub_adr = self.primary[-8:]
        #if self.TPW.cloud_access_enabled():
        self.TPW.teslaInitializeData()
        teslaPWSetupNode(self.poly, self.primary, 'setup_'+sub_adr, 'Setup PW Parameters', self.TPW)
        if self.TPW.solarInstalled:
            teslaPWSolarNode(self.poly, self.primary, 'solar_'+sub_adr, 'Solar Status', self.TPW)
        if self.TPW.generatorInstalled:
            teslaPWGenNode(self.poly, self.primary, 'extpwr'+sub_adr, 'Generator Status', self.TPW)
        teslaPWHistoryNode(self.poly, self.primary, 'hist_'+sub_adr, 'History', self.TPW)


        self.TPW.teslaInitializeData()
        self.updateISYdrivers()
        self.node_ok = True

    def stop(self):
        logging.debug('stop - Cleaning up')
    
    def node_ready(self):
        return(self.node_ok)


    def PW_setDriver(self, key, value, Unit=None):
        logging.debug('PW_setDriver : {} {} {}'.format(key, value, Unit))
        if value == None:
            logging.debug('None value passed = seting 99, UOM 25')
            self.node.setDriver(key, 99, False, False, 25)
        else:
            if Unit:
                self.node.setDriver(key, value, False, False, Unit)
            else:
                self.node.setDriver(key, value)

    def updateISYdrivers(self):


        logging.debug('StatusNode updateISYdrivers')
        #tmp = self.TPW.getTPW_backup_time_remaining()
        #logging.debug('GV0: {}'.format(tmp))
        self.PW_setDriver('ST', self.bool2ISY(self.TPW.getTPW_onLine()))

        self.PW_setDriver('GV0', round(self.TPW.getTPW_chargeLevel(),1))
     
        self.PW_setDriver('GV1', self.TPW.getTPW_chargeLevel())

        self.PW_setDriver('GV2', self.TPW.getTPW_operationMode())

        self.node.setDriver('GV7', self.TPW.getTPW_daysBattery())
        self.node.setDriver('GV8', self.TPW.getTPW_yesterdayBattery())
        self.node.setDriver('GV10', self.TPW.getTPW_daysGrid())
        self.node.setDriver('GV11', self.TPW.getTPW_yesterdayGrid())
        self.node.setDriver('GV13', self.TPW.getTPW_daysConsumption())
        self.node.setDriver('GV14', self.TPW.getTPW_yesterdayConsumption())
        self.node.setDriver('GV15', self.TPW.getTPW_daysGeneration())
        self.node.setDriver('GV16', self.TPW.getTPW_yesterdayGeneration())
        self.node.setDriver('GV17', self.TPW.getTPW_daysGridServicesUse())
        self.node.setDriver('GV18', self.TPW.getTPW_yesterdayGridServicesUse())
        self.node.setDriver('GV17', self.TPW.getTPW_daysSolar())
        self.node.setDriver('GV20', self.TPW.getTPW_yesterdaySolar())
        self.node.setDriver('GV21', self.TPW.getTPW_days_backup_events())
        self.node.setDriver('GV22', self.TPW.getTPW_days_backup_time())
        self.node.setDriver('GV23', self.TPW.getTPW_yesterday_backup_events())
        self.node.setDriver('GV24', self.TPW.getTPW_yesterday_backup_time())

        
        #self.PW_setDriver('GV3', self.TPW.)
        
        #self.PW_setDriver('GV4', self.TPW.)

        #self.PW_setDriver('GV5', self.TPW.)

        #self.PW_setDriver('GV6', self.TPW.)

        #self.PW_setDriver('GV7', self.TPW.)
        #self.PW_setDriver('GV8', self.TPW.)

        #self.PW_setDriver('GV9', self.TPW.)

        #self.PW_setDriver('GV10', self.TPW.)

        #self.PW_setDriver('GV11', self.TPW.)

        #self.PW_setDriver('GV12', self.TPW.)
        #self.PW_setDriver('GV13', self.TPW.getTPW_chargeLevel())
        #self.PW_setDriver('GV14', self.TPW.getTPW_gridSupply())
        #self.PW_setDriver('GV15', self.TPW.getTPW_load())
        

        #self.PW_setDriver('GV16', self.TPW.)

        #self.PW_setDriver('GV17', self.TPW.)

        #self.PW_setDriver('GV18', self.TPW.)

        #self.PW_setDriver('GV19', self.TPW.)

        #self.PW_setDriver('GV20', self.TPW.)
        #self.PW_setDriver('GV21', self.TPW.)

        #self.PW_setDriver('GV22', self.TPW.)

        #self.PW_setDriver('GV23', self.TPW.)

        #self.PW_setDriver('GV24', self.TPW.)

        #self.PW_setDriver('GV25', self.TPW.)

        #self.PW_setDriver('GV26', self.TPW.)

        #self.PW_setDriver('GV27', self.TPW.)

        #self.PW_setDriver('GV28', self.TPW.)

        #self.PW_setDriver('GV29', self.TPW.)
        
        self.PW_setDriver('GV7', self.TPW.getTPW_daysBattery())
        #self.PW_setDriver('GV8', self.TPW.getTPW_yesterdayBattery())
        self.PW_setDriver('GV10', self.TPW.getTPW_daysGrid())
        #self.PW_setDriver('GV11', self.TPW.getTPW_yesterdayGrid())
        self.PW_setDriver('GV13', self.TPW.getTPW_daysConsumption())
        #self.PW_setDriver('GV14', self.TPW.getTPW_yesterdayConsumption())
        self.PW_setDriver('GV15', self.TPW.getTPW_daysGeneration())
        #self.PW_setDriver('GV16', self.TPW.getTPW_yesterdayGeneration())
        self.PW_setDriver('GV17', self.TPW.getTPW_daysGridServicesUse())
        #self.PW_setDriver('GV18', self.TPW.getTPW_yesterdayGridServicesUse())
        self.PW_setDriver('GV17', self.TPW.getTPW_daysSolar())
        #self.PW_setDriver('GV20', self.TPW.getTPW_yesterdaySolar())
        


    def update_PW_data(self, level):
        self.TPW.pollSystemData(level) 


    def ISYupdate (self, command):
        logging.debug('ISY-update called')
        self.update_PW_data('all')
        self.updateISYdrivers()

 

    id = 'pwstatus'
    commands = { 'UPDATE': ISYupdate, 
                }
    '''
    ST-nlspwstatus-ST-NAME = Connected to Tesla
    ST-nlspwstatus-GV0-NAME = Remaining Battery 
    ST-nlspwstatus-GV1-NAME = Inst Solar Export
    ST-nlspwstatus-GV2-NAME = Inst Battery Export
    ST-nlspwstatus-GV3-NAME = Inst Home Load
    ST-nlspwstatus-GV4-NAME = Inst Grid Import

    ST-nlspwstatus-GV5-NAME = Operation Mode
    ST-nlspwstatus-GV6-NAME = Grid Status
    ST-nlspwstatus-GV7-NAME = Grid Services Active

    ST-nlspwstatus-GV8-NAME = Home Total Use Today
    ST-nlspwstatus-GV9-NAME = Solar Export Today
    ST-nlspwstatus-GV10-NAME = Battery Export Today
    ST-nlspwstatus-GV11-NAME = Battery Import Today
    ST-nlspwstatus-GV12-NAME = Grid Import Today
    ST-nlspwstatus-GV13-NAME= Grid Export Today
    ST-nlspwstatus-GV14-NAME = Grid Service Today

    ST-nlspwstatus-GV15-NAME = Home Total Use Yesterday
    ST-nlspwstatus-GV16-NAME = Solar Export Yesterday
    ST-nlspwstatus-GV17-NAME = Battery Export Yesterday
    ST-nlspwstatus-GV18-NAME = Battery Import Yesterday
    ST-nlspwstatus-GV19-NAME = Grid Import Yesterday
    ST-nlspwstatus-GV20-NAME= Grid Export Yesterday
    ST-nlspwstatus-GV21-NAME = Grid Service Yesterday

    ST-nlspwstatus-GV22-NAME = Today nbr backup events 
    ST-nlspwstatus-GV23-NAME = Today backup event time
    ST-nlspwstatus-GV24-NAME = Yesterday nbr backup events 
    ST-nlspwstatus-GV25-NAME = Yesterday backup event time
    ST-nlspwstatus-GV26-NAME = Today charge power
    ST-nlspwstatus-GV27-NAME = Today charge time
    ST-nlspwstatus-GV28-NAME = Yesterday charge power
    ST-nlspwstatus-GV29-NAME = Yesterday charge time

    '''

    drivers = [
            {'driver': 'ST', 'value': 99, 'uom': 25},  #online         
            {'driver': 'GV0', 'value': 0, 'uom': 51},       
            {'driver': 'GV1', 'value': 0, 'uom': 33},
            {'driver': 'GV2', 'value': 0, 'uom': 33},  
            {'driver': 'GV3', 'value': 0, 'uom': 33}, 
            {'driver': 'GV4', 'value': 0, 'uom': 33},  

            {'driver': 'GV5', 'value': 99, 'uom': 25},  
            {'driver': 'GV6', 'value': 99, 'uom': 25},  
            {'driver': 'GV7', 'value': 99, 'uom': 25},  

            {'driver': 'GV8', 'value': 99, 'uom': 25}, 
            {'driver': 'GV9', 'value': 0, 'uom': 33}, 
            {'driver': 'GV10', 'value': 0, 'uom': 33},  
            {'driver': 'GV11', 'value': 0, 'uom': 33},  
            {'driver': 'GV12', 'value': 0, 'uom': 33},
            {'driver': 'GV13', 'value': 0, 'uom': 33}, 
            {'driver': 'GV14', 'value': 0, 'uom': 33}, 
            {'driver': 'GV15', 'value': 0, 'uom': 33},
            
            #{'driver': 'GV16', 'value': 0, 'uom': 33}, 
            #{'driver': 'GV17', 'value': 0, 'uom': 33}, 
            #{'driver': 'GV18', 'value': 0, 'uom': 33}, 
            #{'driver': 'GV19', 'value': 0, 'uom': 33}, 
            #{'driver': 'GV20', 'value': 0, 'uom': 33}, 
            #{'driver': 'GV21', 'value': 0, 'uom': 33},
            #{'driver': 'GV22', 'value': 0, 'uom': 0},
            #{'driver': 'GV23', 'value': 0, 'uom': 58},
            #{'driver': 'GV24', 'value': 0, 'uom': 0}, 
            #{'driver': 'GV25', 'value': 0, 'uom': 58}, 
            #{'driver': 'GV26', 'value': 99, 'uom': 33},
            #{'driver': 'GV27', 'value': 99, 'uom': 58}, 
            #{'driver': 'GV28', 'value': 99, 'uom': 33},
            #{'driver': 'GV28', 'value': 99, 'uom': 58},    
                     
            ]

    
