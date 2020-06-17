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

    $hotColdIconImg = "";
    $hotColdIconImg17 = "";

    function setGet($argsStr)
    {
        global $pythonSetGetScript;
        global $TimeOfDayToStart, $TimeOfDayToStop, $SwitchOnTemp, $SwitchOffTemp;
        global $SmartPlugIpAddr;
        global $MinTimeBetweenChangingSwitchState, $MinTimeBetweenRetryingSwitchChange, $TimeBetweenTempCheck;
        global $InvalidTempLow, $InvalidTempHigh;
        global $SwitchStateAfterTimeOfDayStop;
        global $DeviceName, $DeviceColor;
        global $currentTemperature, $switchState;
        global $hotColdIconImg, $hotColdIconImg17;

        $curSettings = shell_exec($pythonSetGetScript.$argsStr);
        $curSettings_arr = explode ("|", $curSettings);

        $TimeOfDayToStart = $curSettings_arr[0];
        $TimeOfDayToStop  = $curSettings_arr[1];
        $SwitchOnTemp     = $curSettings_arr[2];
        $SwitchOffTemp    = $curSettings_arr[3];

        $SmartPlugIpAddr = $curSettings_arr[4];

        $MinTimeBetweenChangingSwitchState  = $curSettings_arr[5];
        $MinTimeBetweenRetryingSwitchChange = $curSettings_arr[6];
        $TimeBetweenTempCheck               = $curSettings_arr[7];

        $InvalidTempLow  = $curSettings_arr[8];
        $InvalidTempHigh = $curSettings_arr[9];

        $SwitchStateAfterTimeOfDayStop = $curSettings_arr[10];

        $DeviceName = $curSettings_arr[11];
        $DeviceColor = $curSettings_arr[12];

        $currentTemperature = $curSettings_arr[13]."° F";
        $switchState = $curSettings_arr[14];

        $hotColdIconImg = "";
        if($SwitchOnTemp < $SwitchOffTemp)
        {
            $hotColdIconImg = "hot.png";
            if($switchState == "On"){
                $hotColdIconImg17 = "hot.17.color.png";
            } else {
                $hotColdIconImg17 = "hot.17.gray.png";
            }
        }
        elseif($SwitchOnTemp > $SwitchOffTemp)
        {
            $hotColdIconImg = "cold.png";
            if($switchState == "On"){
                $hotColdIconImg17 = "cold.17.color.png";
            } else {
                $hotColdIconImg17 = "cold.17.gray.png";
            }
        }
    }

?>
