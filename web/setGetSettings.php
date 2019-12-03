<?php
    $pythonSetGetScript = 'python /home/pi/thermo/changeSettings.py';

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

    $currentTemperature = "";
    $switchState  = "";

    $currentTemperature = "";
    $switchState  = "";

    $hotColdIconImg = "";

    function setGet($argsStr)
    {
        global $pythonSetGetScript;
        global $TimeOfDayToStart, $TimeOfDayToStop, $SwitchOnTemp, $SwitchOffTemp;
        global $SmartPlugIpAddr;
        global $MinTimeBetweenChangingSwitchState, $MinTimeBetweenRetryingSwitchChange, $TimeBetweenTempCheck;
        global $InvalidTempLow, $InvalidTempHigh;
        global $SwitchStateAfterTimeOfDayStop;
        global $currentTemperature, $switchState;
        global $hotColdIconImg;

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

        $currentTemperature = $curSettings_arr[11]."° F";
        $switchState = $curSettings_arr[12];

        $hotColdIconImg = "";
        if($SwitchOnTemp < $SwitchOffTemp)
        {
            $hotColdIconImg = "hot.png";
        }
        elseif($SwitchOnTemp > $SwitchOffTemp)
        {
            $hotColdIconImg = "cold.png";
        }
    }

?>
