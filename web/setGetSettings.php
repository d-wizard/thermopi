<?php
    $thisScriptDir = dirname(__FILE__);
    $thermoPythonDir = $thisScriptDir."/../"; # The directory with all the python scripts is up one directory from this script.
    $pythonSetGetScript = "python ".$thermoPythonDir."/changeSettings.py";

    // 
    $TimeOfDayToStart = "";
    $TimeOfDayToStop  = "";
    $SwitchOnTemp     = "";
    $SwitchOffTemp    = "";

    $SmartPlugIpAddr = "";

    $MinTimeBetweenChangingSwitchState = "";
    $MinTimeBetweenRetryingSwitchChange = "";
    $TimeBetweenTempCheck = "";

    $InvalidTempLow = "";
    $InvalidTempHigh = "";

    $SwitchStateAfterTimeOfDayStop = "";

    $DeviceName = "";
    $DeviceColor = "";

    $currentTemperature = "";
    $switchState  = "";

    $currentTemperature = "";
    $switchState  = "";

    $hotColdIconImg17 = "";
    $hotColdIconImg48 = "";
    $hotColdIconImgIcon = "";

    function setGet($argsStr)
    {
        global $pythonSetGetScript;
        global $TimeOfDayToStart, $TimeOfDayToStop;
        global $SwitchTemperature, $SwitchComfortRange, $SwitchHeatCool;
        global $SmartPlugIpAddr;
        global $MinTimeBetweenChangingSwitchState, $MinTimeBetweenRetryingSwitchChange, $TimeBetweenTempCheck;
        global $InvalidTempLow, $InvalidTempHigh;
        global $SwitchStateAfterTimeOfDayStop;
        global $DeviceName, $DeviceColor;
        global $currentTemperature, $switchState;
        global $hotColdIconImg17, $hotColdIconImg48, $hotColdIconImgIcon;

        $curSettings = shell_exec($pythonSetGetScript.$argsStr);
        $curSettings_arr = explode ("|", $curSettings);

        // Pull out all the settings printed by the python script.
        $inArrCnt = 0;
        $TimeOfDayToStart                   = $curSettings_arr[$inArrCnt++];
        $TimeOfDayToStop                    = $curSettings_arr[$inArrCnt++];
        $SwitchTemperature                  = $curSettings_arr[$inArrCnt++];
        $SwitchComfortRange                 = $curSettings_arr[$inArrCnt++];
        $SwitchHeatCool                     = $curSettings_arr[$inArrCnt++];
        $SmartPlugIpAddr                    = $curSettings_arr[$inArrCnt++];
        $MinTimeBetweenChangingSwitchState  = $curSettings_arr[$inArrCnt++];
        $MinTimeBetweenRetryingSwitchChange = $curSettings_arr[$inArrCnt++];
        $TimeBetweenTempCheck               = $curSettings_arr[$inArrCnt++];
        $InvalidTempLow                     = $curSettings_arr[$inArrCnt++];
        $InvalidTempHigh                    = $curSettings_arr[$inArrCnt++];
        $SwitchStateAfterTimeOfDayStop      = $curSettings_arr[$inArrCnt++];
        $DeviceName                         = $curSettings_arr[$inArrCnt++];
        $DeviceColor                        = $curSettings_arr[$inArrCnt++];
        $currentTemperature                 = $curSettings_arr[$inArrCnt++]."° F";
        $switchState                        = $curSettings_arr[$inArrCnt++];

        // Determine which icons to use.
        $hotColdIconImg17 = "";
        $hotColdIconImg48 = "";
        $hotColdIconImgIcon = "";
        if($SwitchHeatCool > 0)
        {
            if($switchState == "On"){
                $hotColdIconImg17 = "hot.17.color.png";
                $hotColdIconImg48 = "hot.48.color.png"; 
            } else {
                $hotColdIconImg17 = "hot.17.gray.png";
                $hotColdIconImg48 = "hot.48.gray.png"; 
            }
        }
        elseif($SwitchHeatCool < 0)
        {
            if($switchState == "On"){
                $hotColdIconImg17 = "cold.17.color.png";
                $hotColdIconImg48 = "cold.48.color.png"; 
            } else {
                $hotColdIconImg17 = "cold.17.gray.png";
                $hotColdIconImg48 = "cold.48.gray.png"; 
            }
        }
        $hotColdIconImgIcon = $hotColdIconImg48;
    }

?>
