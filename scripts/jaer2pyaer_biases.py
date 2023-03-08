"""
Reads a jAER .xml biases file and produces the matching pyaer/libcaer .json file to load the jAER biases
"""
import os
import sys

from  pyaer.get_logger import get_logger
log=get_logger()
from typing import Tuple, Union, Optional
import re
from easygui import fileopenbox, filesavebox
from pyaer.prefs import MyPreferences
from pyaer.utils import load_json

def get_jaer_key(pyaer_key:str, jaer_line:str)->Optional[re.Match]:
    jaer_key=None
    flip_coarse_val=False
    if pyaer_key == 'exposure':
        jaer_key = 'APS\.Exposure'
    elif pyaer_key == 'autoexposure':
        jaer_key = r'APS\.Exposure'
    elif pyaer_key == r'frame_interval':
        jaer_key = r'APS\.FrameInterval'
    elif pyaer_key == r'frame_interval':
        jaer_key = 'APS\.FrameDelay'
    elif pyaer_key == 'exposure':
        jaer_key = 'APS\.Exposure'
    elif pyaer_key == 'imu_enabled':
        jaer_key = 'IMU\.Run'
    elif pyaer_key == 'imu_acc_scale':
        jaer_key = 'IMU\.AccelFullScale'
    elif pyaer_key == 'imu_gyro_scale':
        jaer_key = 'IMU\.GyroFullScale'
    elif pyaer_key == 'imu_low_pass_filter':
        jaer_key = 'IMU\.DigitalLowPassFilter'
    elif pyaer_key == 'background_activity_filter_enabled':
        jaer_key = 'DVS\.FilterBackgroundActivity'
    elif pyaer_key == 'background_activity_filter_time':
        jaer_key = 'DVS\.FilterBackgroundActivityDeltaTime'
    elif pyaer_key == 'refractory_period_enabled':
        jaer_key = 'DVS\.FilterRefractoryPeriod'
    elif pyaer_key == 'refractory_period_time':
        jaer_key = 'DVS\.FilterRefractoryPeriodTime'
    else: # key like BiasBuffer_fine
        parts=pyaer_key.split('_') # e.g. PadFollBn and coarse
        if len(parts)<2:
            return None
        elif len(parts)==2:
            bias=parts[0]
            type=parts[1]
        elif len(parts)==3:
            bias=parts[0]+'_'+parts[1]
            type=parts[2]
        else:
            raise ValueError(f'{pyaer_key} has too many underscores')
        if type=='coarse':
            jaer_key=bias+'.BitValueCoarse'
            flip_coarse_val=True
        elif type=='fine':
            jaer_key=bias+'.BitValueFine'
        elif type=='volt':
            jaer_key=bias+r'.VdacBitValue'
        elif type=='curr':
            jaer_key=bias+'.BufBitValue'
        elif type=='enabled':
            jaer_key=bias+'.Run'

    if jaer_key is None: return None

    jaer_key+='"' # closing " of entry key=""
    if re.search(jaer_key,jaer_line,re.IGNORECASE): # if line has the jaer key
        p=re.compile(r'.*value="(\w*)"') # find the value
        m=p.search(jaer_line)
        if m is None: return None
        value=m.group(1) # now obtain it
        if flip_coarse_val: # coarse val must be flipped because jaer sends the hardware value which is flipped on chip
            value=str(7-int(value))
    # whole_key=re.compile(whole_key_pat,re.IGNORECASE| re.VERBOSE | re.ASCII)
    #     log.debug(f'for pyaer_key={pyaer_key} found jaer_key={jaer_key} with value={value}')
        return value
    else:
        # log.debug(f'no match for pyaer_key={pyaer_key} to jaer_key={jaer_key} in jaer_line={jaer_line}')
        return None

def __main__():
    prefs=MyPreferences()
    lastfile=prefs.get('last_pyaer_json_file',None)
    if lastfile is None:
        lastfile='*.json'
    fn=fileopenbox(msg='select the pyaer biases config .json file',title='pyaer biases config',default=lastfile, filetypes=['*.json'])
    if fn is None:
        print('no file selected')
        sys.exit(0)
    prefs.put('last_pyaer_json_file',fn)
    pyaer_config:dict=load_json(fn)


    lastfile=prefs.get('last_jaer_xml_file',None)
    if lastfile is None:
        lastfile='*.xml'
    fn=fileopenbox(msg='select the jaer biases .xml file',title='jAER Prefs',default=lastfile, filetypes=[['*.xml','jAER biases .xml file']])
    if fn is None:
        print('no file selected')
        sys.exit(0)
    prefs.put('last_jaer_xml_file',fn)
    file=open(fn,'r')
    jaer_lines=file.readlines()
    config_keys=pyaer_config.keys()

    for config_key in config_keys:
        if config_key=='dvs_enabled':
            pass
        if not isinstance(config_key, str):
            continue
        for line in jaer_lines:
            value=get_jaer_key(config_key, line.strip())
            if value:
                print(f'\t"{config_key}": {value},')
                break

if __name__ == "__main__":
    __main__()

"""
bias_name_mapping={
    "ADC_RefHigh_volt": "ADC_RefHigh.VdacBitValue",
    "ADC_RefHigh_curr": "ADC_RefHigh.BufBitValue",
    "ADC_RefLow_volt": "ADC_RefLow.VdacBitValue",
    "ADC_RefLow_curr": "ADC_RefLow.BufBitValue",
    "LocalBufBn_coarse": "LocalBufBn.BitValueCoarse",
    "LocalBufBn_fine": "LocalBufBn.BitValueFine",
    "PadFollBn_coarse": "PadFollBn.BitValueCoarse",
    "PadFollBn_fine": "PadFollBn.BitValueFine",
    "DiffBn_coarse": "DiffBn.BitValueCoarse",
    "DiffBn_fine": "DiffBn.BitValueFine",
    "ONBn_coarse": 3,
    "ONBn_fine": 6,
    "OFFBn_coarse": 2,
    "OFFBn_fine": 220,
    "PixInvBn_coarse": 5,
    "PixInvBn_fine": 129,
    "PrBp_coarse": 2,
    "PrBp_fine": 116,
    "PrSFBp_coarse": 1,
    "PrSFBp_fine": 32,
    "RefrBp_coarse": 4,
    "RefrBp_fine": 25,
    "ReadoutBufBp_coarse": 6,
    "ReadoutBufBp_fine": 20,
    "APSROSFBn_coarse": 6,
    "APSROSFBn_fine": 219,
    "ADCCompBp_coarse": 5,
    "ADCCompBp_fine": 20,
    "COLSELLowBn_coarse": 0,
    "COLSELLowBn_fine": 1,
    "DACBufBp_coarse": 6,
    "DACBufBp_fine": 60,
    "LcolTimeoutBn_coarse": 5,
    "LcolTimeoutBn_fine": 49,
    "AEPdBn_coarse": 6,
    "AEPdBn_fine": 91,
    "AEPuXBp_coarse": 4,
    "AEPuXBp_fine": 80,
    "AEPuYBp_coarse": 7,
    "AEPuYBp_fine": 152,
    "IFRefrBn_coarse": 5,
    "IFRefrBn_fine": 255,
    "IFThrBn_coarse": 5,
    "IFThrBn_fine": 255,
    "BiasBuffer_coarse": 5,
    "BiasBuffer_fine": 254,
    "aps_enabled": false,
    "dvs_enabled": true,
    "exposure": 30000,
    "autoexposure": true,
    "frame_interval": 0,
    "imu_enabled": false,
    "imu_acc_scale": 3,
    "imu_gyro_scale": 3,
    "imu_low_pass_filter": 0,
    "background_activity_filter_enabled": true,
    "background_activity_filter_time": 3000,
    "refractory_period_enabled": false,
    "refractory_period_time": 2,
}
"""

"""
DAVIS XML biases from jAER
<entry key="Davis346B.AERnArow" value="false"/>
<entry key="Davis346B.APS.ADCTestMode" value="false"/>
<entry key="Davis346B.APS.ColumnSettle" value="30"/>
<entry key="Davis346B.APS.Exposure" value="4884"/>
<entry key="Davis346B.APS.FrameDelay" value="1000"/>
<entry key="Davis346B.APS.FrameInterval" value="50000"/>
<entry key="Davis346B.APS.GlobalShutter" value="true"/>
<entry key="Davis346B.APS.NullSettle" value="3"/>
<entry key="Davis346B.APS.RampReset" value="10"/>
<entry key="Davis346B.APS.RampShortReset" value="false"/>
<entry key="Davis346B.APS.ResetRead" value="true"/>
<entry key="Davis346B.APS.ResetSettle" value="10"/>
<entry key="Davis346B.APS.RowSettle" value="10"/>
<entry key="Davis346B.APS.Run" value="false"/>
<entry key="Davis346B.APS.SampleEnable" value="true"/>
<entry key="Davis346B.APS.SampleSettle" value="30"/>
<entry key="Davis346B.APS.UseInternalADC" value="true"/>
<entry key="Davis346B.APS.WaitOnTransferStall" value="true"/>
<entry key="Davis346B.AddressedIPotCF.ADCcompBp.BitValueCoarse" value="2"/>
<entry key="Davis346B.AddressedIPotCF.ADCcompBp.BitValueFine" value="20"/>
<entry key="Davis346B.AddressedIPotCF.ADCcompBp.Enabled" value="true"/>
<entry key="Davis346B.AddressedIPotCF.ADCcompBp.LowCurrent" value="false"/>
<entry key="Davis346B.AddressedIPotCF.ADCcompBp.Sex" value="P"/>
<entry key="Davis346B.AddressedIPotCF.ADCcompBp.Type" value="NORMAL"/>
<entry key="Davis346B.AddressedIPotCF.AEPdBn.BitValueCoarse" value="1"/>
<entry key="Davis346B.AddressedIPotCF.AEPdBn.BitValueFine" value="91"/>
<entry key="Davis346B.AddressedIPotCF.AEPdBn.Enabled" value="true"/>
<entry key="Davis346B.AddressedIPotCF.AEPdBn.LowCurrent" value="false"/>
<entry key="Davis346B.AddressedIPotCF.AEPdBn.Sex" value="N"/>
<entry key="Davis346B.AddressedIPotCF.AEPdBn.Type" value="NORMAL"/>
<entry key="Davis346B.AddressedIPotCF.AEPuXBp.BitValueCoarse" value="3"/>
<entry key="Davis346B.AddressedIPotCF.AEPuXBp.BitValueFine" value="80"/>
<entry key="Davis346B.AddressedIPotCF.AEPuXBp.Enabled" value="true"/>
<entry key="Davis346B.AddressedIPotCF.AEPuXBp.LowCurrent" value="false"/>
<entry key="Davis346B.AddressedIPotCF.AEPuXBp.Sex" value="P"/>
<entry key="Davis346B.AddressedIPotCF.AEPuXBp.Type" value="NORMAL"/>
<entry key="Davis346B.AddressedIPotCF.AEPuYBp.BitValueCoarse" value="0"/>
<entry key="Davis346B.AddressedIPotCF.AEPuYBp.BitValueFine" value="152"/>
<entry key="Davis346B.AddressedIPotCF.AEPuYBp.Enabled" value="true"/>
<entry key="Davis346B.AddressedIPotCF.AEPuYBp.LowCurrent" value="false"/>
<entry key="Davis346B.AddressedIPotCF.AEPuYBp.Sex" value="P"/>
<entry key="Davis346B.AddressedIPotCF.AEPuYBp.Type" value="NORMAL"/>
<entry key="Davis346B.AddressedIPotCF.ApsROSFBn.BitValueCoarse" value="1"/>
<entry key="Davis346B.AddressedIPotCF.ApsROSFBn.BitValueFine" value="219"/>
<entry key="Davis346B.AddressedIPotCF.ApsROSFBn.Enabled" value="true"/>
<entry key="Davis346B.AddressedIPotCF.ApsROSFBn.LowCurrent" value="false"/>
<entry key="Davis346B.AddressedIPotCF.ApsROSFBn.Sex" value="N"/>
<entry key="Davis346B.AddressedIPotCF.ApsROSFBn.Type" value="NORMAL"/>
<entry key="Davis346B.AddressedIPotCF.Blk1N.BitValueCoarse" value="0"/>
<entry key="Davis346B.AddressedIPotCF.Blk1N.BitValueFine" value="0"/>
<entry key="Davis346B.AddressedIPotCF.Blk1N.Enabled" value="true"/>
<entry key="Davis346B.AddressedIPotCF.Blk1N.LowCurrent" value="false"/>
<entry key="Davis346B.AddressedIPotCF.Blk1N.Sex" value="N"/>
<entry key="Davis346B.AddressedIPotCF.Blk1N.Type" value="NORMAL"/>
<entry key="Davis346B.AddressedIPotCF.Blk1P.BitValueCoarse" value="0"/>
<entry key="Davis346B.AddressedIPotCF.Blk1P.BitValueFine" value="0"/>
<entry key="Davis346B.AddressedIPotCF.Blk1P.Enabled" value="true"/>
<entry key="Davis346B.AddressedIPotCF.Blk1P.LowCurrent" value="false"/>
<entry key="Davis346B.AddressedIPotCF.Blk1P.Sex" value="P"/>
<entry key="Davis346B.AddressedIPotCF.Blk1P.Type" value="NORMAL"/>
<entry key="Davis346B.AddressedIPotCF.Blk2N.BitValueCoarse" value="0"/>
<entry key="Davis346B.AddressedIPotCF.Blk2N.BitValueFine" value="0"/>
<entry key="Davis346B.AddressedIPotCF.Blk2N.Enabled" value="true"/>
<entry key="Davis346B.AddressedIPotCF.Blk2N.LowCurrent" value="false"/>
<entry key="Davis346B.AddressedIPotCF.Blk2N.Sex" value="N"/>
<entry key="Davis346B.AddressedIPotCF.Blk2N.Type" value="NORMAL"/>
<entry key="Davis346B.AddressedIPotCF.Blk2P.BitValueCoarse" value="0"/>
<entry key="Davis346B.AddressedIPotCF.Blk2P.BitValueFine" value="0"/>
<entry key="Davis346B.AddressedIPotCF.Blk2P.Enabled" value="true"/>
<entry key="Davis346B.AddressedIPotCF.Blk2P.LowCurrent" value="false"/>
<entry key="Davis346B.AddressedIPotCF.Blk2P.Sex" value="P"/>
<entry key="Davis346B.AddressedIPotCF.Blk2P.Type" value="NORMAL"/>
<entry key="Davis346B.AddressedIPotCF.Blk3N.BitValueCoarse" value="0"/>
<entry key="Davis346B.AddressedIPotCF.Blk3N.BitValueFine" value="0"/>
<entry key="Davis346B.AddressedIPotCF.Blk3N.Enabled" value="true"/>
<entry key="Davis346B.AddressedIPotCF.Blk3N.LowCurrent" value="false"/>
<entry key="Davis346B.AddressedIPotCF.Blk3N.Sex" value="N"/>
<entry key="Davis346B.AddressedIPotCF.Blk3N.Type" value="NORMAL"/>
<entry key="Davis346B.AddressedIPotCF.Blk4N.BitValueCoarse" value="0"/>
<entry key="Davis346B.AddressedIPotCF.Blk4N.BitValueFine" value="0"/>
<entry key="Davis346B.AddressedIPotCF.Blk4N.Enabled" value="true"/>
<entry key="Davis346B.AddressedIPotCF.Blk4N.LowCurrent" value="false"/>
<entry key="Davis346B.AddressedIPotCF.Blk4N.Sex" value="N"/>
<entry key="Davis346B.AddressedIPotCF.Blk4N.Type" value="NORMAL"/>
<entry key="Davis346B.AddressedIPotCF.ColSelLowBn.BitValueCoarse" value="7"/>
<entry key="Davis346B.AddressedIPotCF.ColSelLowBn.BitValueFine" value="1"/>
<entry key="Davis346B.AddressedIPotCF.ColSelLowBn.Enabled" value="true"/>
<entry key="Davis346B.AddressedIPotCF.ColSelLowBn.LowCurrent" value="false"/>
<entry key="Davis346B.AddressedIPotCF.ColSelLowBn.Sex" value="N"/>
<entry key="Davis346B.AddressedIPotCF.ColSelLowBn.Type" value="NORMAL"/>
<entry key="Davis346B.AddressedIPotCF.DACBufBp.BitValueCoarse" value="1"/>
<entry key="Davis346B.AddressedIPotCF.DACBufBp.BitValueFine" value="60"/>
<entry key="Davis346B.AddressedIPotCF.DACBufBp.Enabled" value="true"/>
<entry key="Davis346B.AddressedIPotCF.DACBufBp.LowCurrent" value="false"/>
<entry key="Davis346B.AddressedIPotCF.DACBufBp.Sex" value="P"/>
<entry key="Davis346B.AddressedIPotCF.DACBufBp.Type" value="NORMAL"/>
<entry key="Davis346B.AddressedIPotCF.DiffBn.BitValueCoarse" value="3"/>
<entry key="Davis346B.AddressedIPotCF.DiffBn.BitValueFine" value="39"/>
<entry key="Davis346B.AddressedIPotCF.DiffBn.Enabled" value="true"/>
<entry key="Davis346B.AddressedIPotCF.DiffBn.LowCurrent" value="false"/>
<entry key="Davis346B.AddressedIPotCF.DiffBn.Sex" value="N"/>
<entry key="Davis346B.AddressedIPotCF.DiffBn.Type" value="NORMAL"/>
<entry key="Davis346B.AddressedIPotCF.IFRefrBn.BitValueCoarse" value="2"/>
<entry key="Davis346B.AddressedIPotCF.IFRefrBn.BitValueFine" value="255"/>
<entry key="Davis346B.AddressedIPotCF.IFRefrBn.Enabled" value="true"/>
<entry key="Davis346B.AddressedIPotCF.IFRefrBn.LowCurrent" value="false"/>
<entry key="Davis346B.AddressedIPotCF.IFRefrBn.Sex" value="N"/>
<entry key="Davis346B.AddressedIPotCF.IFRefrBn.Type" value="NORMAL"/>
<entry key="Davis346B.AddressedIPotCF.IFThrBn.BitValueCoarse" value="2"/>
<entry key="Davis346B.AddressedIPotCF.IFThrBn.BitValueFine" value="255"/>
<entry key="Davis346B.AddressedIPotCF.IFThrBn.Enabled" value="true"/>
<entry key="Davis346B.AddressedIPotCF.IFThrBn.LowCurrent" value="false"/>
<entry key="Davis346B.AddressedIPotCF.IFThrBn.Sex" value="N"/>
<entry key="Davis346B.AddressedIPotCF.IFThrBn.Type" value="NORMAL"/>
<entry key="Davis346B.AddressedIPotCF.LcolTimeoutBn.BitValueCoarse" value="2"/>
<entry key="Davis346B.AddressedIPotCF.LcolTimeoutBn.BitValueFine" value="49"/>
<entry key="Davis346B.AddressedIPotCF.LcolTimeoutBn.Enabled" value="true"/>
<entry key="Davis346B.AddressedIPotCF.LcolTimeoutBn.LowCurrent" value="false"/>
<entry key="Davis346B.AddressedIPotCF.LcolTimeoutBn.Sex" value="N"/>
<entry key="Davis346B.AddressedIPotCF.LcolTimeoutBn.Type" value="NORMAL"/>
<entry key="Davis346B.AddressedIPotCF.LocalBufBn.BitValueCoarse" value="2"/>
<entry key="Davis346B.AddressedIPotCF.LocalBufBn.BitValueFine" value="164"/>
<entry key="Davis346B.AddressedIPotCF.LocalBufBn.Enabled" value="true"/>
<entry key="Davis346B.AddressedIPotCF.LocalBufBn.LowCurrent" value="false"/>
<entry key="Davis346B.AddressedIPotCF.LocalBufBn.Sex" value="N"/>
<entry key="Davis346B.AddressedIPotCF.LocalBufBn.Type" value="NORMAL"/>
<entry key="Davis346B.AddressedIPotCF.OffBn.BitValueCoarse" value="3"/>
<entry key="Davis346B.AddressedIPotCF.OffBn.BitValueFine" value="6"/>
<entry key="Davis346B.AddressedIPotCF.OffBn.Enabled" value="true"/>
<entry key="Davis346B.AddressedIPotCF.OffBn.LowCurrent" value="false"/>
<entry key="Davis346B.AddressedIPotCF.OffBn.Sex" value="N"/>
<entry key="Davis346B.AddressedIPotCF.OffBn.Type" value="NORMAL"/>
<entry key="Davis346B.AddressedIPotCF.OnBn.BitValueCoarse" value="2"/>
<entry key="Davis346B.AddressedIPotCF.OnBn.BitValueFine" value="83"/>
<entry key="Davis346B.AddressedIPotCF.OnBn.Enabled" value="true"/>
<entry key="Davis346B.AddressedIPotCF.OnBn.LowCurrent" value="false"/>
<entry key="Davis346B.AddressedIPotCF.OnBn.Sex" value="N"/>
<entry key="Davis346B.AddressedIPotCF.OnBn.Type" value="NORMAL"/>
<entry key="Davis346B.AddressedIPotCF.PadFollBn.BitValueCoarse" value="0"/>
<entry key="Davis346B.AddressedIPotCF.PadFollBn.BitValueFine" value="215"/>
<entry key="Davis346B.AddressedIPotCF.PadFollBn.Enabled" value="true"/>
<entry key="Davis346B.AddressedIPotCF.PadFollBn.LowCurrent" value="false"/>
<entry key="Davis346B.AddressedIPotCF.PadFollBn.Sex" value="N"/>
<entry key="Davis346B.AddressedIPotCF.PadFollBn.Type" value="NORMAL"/>
<entry key="Davis346B.AddressedIPotCF.PixInvBn.BitValueCoarse" value="2"/>
<entry key="Davis346B.AddressedIPotCF.PixInvBn.BitValueFine" value="129"/>
<entry key="Davis346B.AddressedIPotCF.PixInvBn.Enabled" value="true"/>
<entry key="Davis346B.AddressedIPotCF.PixInvBn.LowCurrent" value="false"/>
<entry key="Davis346B.AddressedIPotCF.PixInvBn.Sex" value="N"/>
<entry key="Davis346B.AddressedIPotCF.PixInvBn.Type" value="NORMAL"/>
<entry key="Davis346B.AddressedIPotCF.PrBp.BitValueCoarse" value="5"/>
<entry key="Davis346B.AddressedIPotCF.PrBp.BitValueFine" value="58"/>
<entry key="Davis346B.AddressedIPotCF.PrBp.Enabled" value="true"/>
<entry key="Davis346B.AddressedIPotCF.PrBp.LowCurrent" value="false"/>
<entry key="Davis346B.AddressedIPotCF.PrBp.Sex" value="P"/>
<entry key="Davis346B.AddressedIPotCF.PrBp.Type" value="NORMAL"/>
<entry key="Davis346B.AddressedIPotCF.PrSFBp.BitValueCoarse" value="6"/>
<entry key="Davis346B.AddressedIPotCF.PrSFBp.BitValueFine" value="16"/>
<entry key="Davis346B.AddressedIPotCF.PrSFBp.Enabled" value="true"/>
<entry key="Davis346B.AddressedIPotCF.PrSFBp.LowCurrent" value="false"/>
<entry key="Davis346B.AddressedIPotCF.PrSFBp.Sex" value="P"/>
<entry key="Davis346B.AddressedIPotCF.PrSFBp.Type" value="NORMAL"/>
<entry key="Davis346B.AddressedIPotCF.ReadoutBufBP.BitValueCoarse" value="1"/>
<entry key="Davis346B.AddressedIPotCF.ReadoutBufBP.BitValueFine" value="20"/>
<entry key="Davis346B.AddressedIPotCF.ReadoutBufBP.Enabled" value="true"/>
<entry key="Davis346B.AddressedIPotCF.ReadoutBufBP.LowCurrent" value="false"/>
<entry key="Davis346B.AddressedIPotCF.ReadoutBufBP.Sex" value="P"/>
<entry key="Davis346B.AddressedIPotCF.ReadoutBufBP.Type" value="NORMAL"/>
<entry key="Davis346B.AddressedIPotCF.RefrBp.BitValueCoarse" value="3"/>
<entry key="Davis346B.AddressedIPotCF.RefrBp.BitValueFine" value="25"/>
<entry key="Davis346B.AddressedIPotCF.RefrBp.Enabled" value="true"/>
<entry key="Davis346B.AddressedIPotCF.RefrBp.LowCurrent" value="false"/>
<entry key="Davis346B.AddressedIPotCF.RefrBp.Sex" value="P"/>
<entry key="Davis346B.AddressedIPotCF.RefrBp.Type" value="NORMAL"/>
<entry key="Davis346B.AddressedIPotCF.biasBuffer.BitValueCoarse" value="2"/>
<entry key="Davis346B.AddressedIPotCF.biasBuffer.BitValueFine" value="254"/>
<entry key="Davis346B.AddressedIPotCF.biasBuffer.Enabled" value="true"/>
<entry key="Davis346B.AddressedIPotCF.biasBuffer.LowCurrent" value="false"/>
<entry key="Davis346B.AddressedIPotCF.biasBuffer.Sex" value="N"/>
<entry key="Davis346B.AddressedIPotCF.biasBuffer.Type" value="NORMAL"/>
<entry key="Davis346B.Chip.AERnArow" value="false"/>
<entry key="Davis346B.Chip.AnalogMux0" value="0"/>
<entry key="Davis346B.Chip.AnalogMux1" value="0"/>
<entry key="Davis346B.Chip.AnalogMux2" value="0"/>
<entry key="Davis346B.Chip.BiasMux0" value="0"/>
<entry key="Davis346B.Chip.DigitalMux0" value="0"/>
<entry key="Davis346B.Chip.DigitalMux1" value="0"/>
<entry key="Davis346B.Chip.DigitalMux2" value="0"/>
<entry key="Davis346B.Chip.DigitalMux3" value="0"/>
<entry key="Davis346B.Chip.ResetCalibNeuron" value="true"/>
<entry key="Davis346B.Chip.ResetTestPixel" value="true"/>
<entry key="Davis346B.Chip.SelectGrayCounter" value="true"/>
<entry key="Davis346B.Chip.TestADC" value="false"/>
<entry key="Davis346B.Chip.TypeNCalibNeuron" value="false"/>
<entry key="Davis346B.Chip.UseAOut" value="false"/>
<entry key="Davis346B.DVS.AckDelayColumn" value="0"/>
<entry key="Davis346B.DVS.AckDelayRow" value="4"/>
<entry key="Davis346B.DVS.AckExtensionColumn" value="0"/>
<entry key="Davis346B.DVS.AckExtensionRow" value="1"/>
<entry key="Davis346B.DVS.ExternalAERControl" value="false"/>
<entry key="Davis346B.DVS.FilterBackgroundActivity" value="false"/>
<entry key="Davis346B.DVS.FilterBackgroundActivityDeltaTime" value="80"/>
<entry key="Davis346B.DVS.FilterPolarityFlatten" value="false"/>
<entry key="Davis346B.DVS.FilterPolaritySuppress" value="false"/>
<entry key="Davis346B.DVS.FilterPolaritySuppressType" value="false"/>
<entry key="Davis346B.DVS.FilterRefractoryPeriod" value="false"/>
<entry key="Davis346B.DVS.FilterRefractoryPeriodTime" value="2"/>
<entry key="Davis346B.DVS.FilterRowOnlyEvents" value="true"/>
<entry key="Davis346B.DVS.FilterSkipEvents" value="false"/>
<entry key="Davis346B.DVS.FilterSkipEventsEvery" value="1"/>
<entry key="Davis346B.DVS.Run" value="true"/>
<entry key="Davis346B.DVS.WaitOnTransferStall" value="false"/>
<entry key="Davis346B.ExtInput.DetectFallingEdges" value="false"/>
<entry key="Davis346B.ExtInput.DetectPulseLength" value="120"/>
<entry key="Davis346B.ExtInput.DetectPulsePolarity" value="true"/>
<entry key="Davis346B.ExtInput.DetectPulses" value="true"/>
<entry key="Davis346B.ExtInput.DetectRisingEdges" value="false"/>
<entry key="Davis346B.ExtInput.GeneratePulseDutyCycle" value="50"/>
<entry key="Davis346B.ExtInput.GeneratePulseFrequency" value="1000000"/>
<entry key="Davis346B.ExtInput.GeneratePulseInterval" value="120"/>
<entry key="Davis346B.ExtInput.GeneratePulseLength" value="60"/>
<entry key="Davis346B.ExtInput.GeneratePulsePolarity" value="false"/>
<entry key="Davis346B.ExtInput.GenerateUseCustomSignal" value="false"/>
<entry key="Davis346B.ExtInput.RunDetector" value="false"/>
<entry key="Davis346B.ExtInput.RunGenerator" value="false"/>
<entry key="Davis346B.GlobalShutter" value="true"/>
<entry key="Davis346B.IMU.AccelFullScale" value="2"/>
<entry key="Davis346B.IMU.AccelScale" value="ImuAccelScaleG8"/>
<entry key="Davis346B.IMU.DigitalLowPassFilter" value="1"/>
<entry key="Davis346B.IMU.GyroFullScale" value="2"/>
<entry key="Davis346B.IMU.GyroScale" value="GyroFullScaleDegPerSec1000"/>
<entry key="Davis346B.IMU.LPCycle" value="false"/>
<entry key="Davis346B.IMU.LPWakeup" value="1"/>
<entry key="Davis346B.IMU.Run" value="false"/>
<entry key="Davis346B.IMU.RunAccel" value="false"/>
<entry key="Davis346B.IMU.RunGyro" value="false"/>
<entry key="Davis346B.IMU.RunTemp" value="false"/>
<entry key="Davis346B.IMU.SampleRateDivider" value="0"/>
<entry key="Davis346B.IMU.TempStandby" value="false"/>
<entry key="Davis346B.IMU.displayEnabled" value="false"/>
<entry key="Davis346B.Masterbias.internalResistorUsed" value="false"/>
<entry key="Davis346B.Masterbias.rint" value="46000.0"/>
<entry key="Davis346B.Masterbias.rx" value="8200.0"/>
<entry key="Davis346B.Mux.DropAPSOnTransferStall" value="false"/>
<entry key="Davis346B.Mux.DropDVSOnTransferStall" value="true"/>
<entry key="Davis346B.Mux.DropExtInputOnTransferStall" value="true"/>
<entry key="Davis346B.Mux.DropIMUOnTransferStall" value="false"/>
<entry key="Davis346B.Mux.ForceChipBiasEnable" value="false"/>
<entry key="Davis346B.Mux.RunChip" value="true"/>
<entry key="Davis346B.ResetCalibNeuron" value="true"/>
<entry key="Davis346B.ResetTestPixel" value="true"/>
<entry key="Davis346B.SelectGrayCounter" value="true"/>
<entry key="Davis346B.ShiftedSourceBias.ADC_RefHigh.BufBitValue" value="7"/>
<entry key="Davis346B.ShiftedSourceBias.ADC_RefHigh.VdacBitValue" value="26"/>
<entry key="Davis346B.ShiftedSourceBias.ADC_RefLow.BufBitValue" value="7"/>
<entry key="Davis346B.ShiftedSourceBias.ADC_RefLow.VdacBitValue" value="1"/>
<entry key="Davis346B.ShiftedSourceBias.AdcTestVoltagexAI.BufBitValue" value="7"/>
<entry key="Davis346B.ShiftedSourceBias.AdcTestVoltagexAI.VdacBitValue" value="0"/>
<entry key="Davis346B.ShiftedSourceBias.ApsCas.BufBitValue" value="6"/>
<entry key="Davis346B.ShiftedSourceBias.ApsCas.VdacBitValue" value="20"/>
<entry key="Davis346B.ShiftedSourceBias.BlkV1.BufBitValue" value="7"/>
<entry key="Davis346B.ShiftedSourceBias.BlkV1.VdacBitValue" value="0"/>
<entry key="Davis346B.ShiftedSourceBias.BlkV2.BufBitValue" value="7"/>
<entry key="Davis346B.ShiftedSourceBias.BlkV2.VdacBitValue" value="0"/>
<entry key="Davis346B.ShiftedSourceBias.BlkV3.BufBitValue" value="7"/>
<entry key="Davis346B.ShiftedSourceBias.BlkV3.VdacBitValue" value="0"/>
<entry key="Davis346B.ShiftedSourceBias.SSN.OperatingMode" value="ShiftedSource"/>
<entry key="Davis346B.ShiftedSourceBias.SSN.RefValue" value="1"/>
<entry key="Davis346B.ShiftedSourceBias.SSN.RegBitValue" value="33"/>
<entry key="Davis346B.ShiftedSourceBias.SSN.VoltageLevel" value="SplitGate"/>
<entry key="Davis346B.ShiftedSourceBias.SSP.OperatingMode" value="ShiftedSource"/>
<entry key="Davis346B.ShiftedSourceBias.SSP.RefValue" value="1"/>
<entry key="Davis346B.ShiftedSourceBias.SSP.RegBitValue" value="33"/>
<entry key="Davis346B.ShiftedSourceBias.SSP.VoltageLevel" value="SplitGate"/>
<entry key="Davis346B.ShiftedSourceBias.apsOverflowLevel.BufBitValue" value="6"/>
<entry key="Davis346B.ShiftedSourceBias.apsOverflowLevel.VdacBitValue" value="23"/>
<entry key="Davis346B.TestADC" value="false"/>
<entry key="Davis346B.TypeNCalibNeuron" value="false"/>
<entry key="Davis346B.USB.EarlyPacketDelay" value="8"/>
<entry key="Davis346B.UseAOut" value="false"/>
<entry key="Davis346B.VDACBias.ADC_RefHigh.BufBitValue" value="7"/>
<entry key="Davis346B.VDACBias.ADC_RefHigh.VdacBitValue" value="30"/>
<entry key="Davis346B.VDACBias.ADC_RefLow.BufBitValue" value="7"/>
<entry key="Davis346B.VDACBias.ADC_RefLow.VdacBitValue" value="1"/>
<entry key="Davis346B.VDACBias.AdcTestVoltage.BufBitValue" value="7"/>
<entry key="Davis346B.VDACBias.AdcTestVoltage.VdacBitValue" value="21"/>
<entry key="Davis346B.VDACBias.ApsCas.BufBitValue" value="6"/>
<entry key="Davis346B.VDACBias.ApsCas.VdacBitValue" value="21"/>
<entry key="Davis346B.VDACBias.apsOverflowLevel.BufBitValue" value="6"/>
<entry key="Davis346B.VDACBias.apsOverflowLevel.VdacBitValue" value="27"/>
<entry key="Davis346B.VideoControl.autoWhiteBalance" value="true"/>
<entry key="Davis346B.VideoControl.colorCorrection" value="true"/>
<entry key="Davis346B.VideoControl.displayEvents" value="true"/>
<entry key="Davis346B.VideoControl.displayFrames" value="false"/>
<entry key="Davis346B.VideoControl.separateAPSByColor" value="false"/>
<entry key="Davis346B.globalShutter" value="false"/>
<entry key="Davis346B.hotPixelSuppression" value="false"/>
<entry key="Davis346B.nArow" value="false"/>
<entry key="Davis346B.nChipReset" value="true"/>
<entry key="Davis346B.powerDown" value="false"/>
<entry key="Davis346B.resetCalib" value="true"/>
<entry key="Davis346B.resetTestpixel" value="true"/>
<entry key="Davis346B.runAdc" value="true"/>
<entry key="Davis346B.runCpld" value="true"/>
<entry key="Davis346B.typeNCalib" value="false"/>
<entry key="Davis346B.useAout" value="true"/>
"""