<html>
<head>
<link rel="stylesheet" type="text/css" href="thermo.css">
<meta name="viewport" content="width=device-width" />
<title>Advanced Settings</title>
</head>
   <body>
   <?php
      /////////////////////////////////////////////////////////
      // This code will run every time something happens.
      /////////////////////////////////////////////////////////
      include 'setGetSettings.php';

      // 
      $timeCmds = array(
         'TimeBetweenTempCheck',
      );

      // 
      $switchCmds = array(
         'SmartPlugIpAddr',
         'MinTimeBetweenChangingSwitchState',
         'MinTimeBetweenRetryingSwitchChange',
         'SwitchStateAfterTimeOfDayStop'
      );

      // 
      $validTempCmds = array(
         'InvalidTempLow',
         'InvalidTempHigh'
      );

      $pyArgsStr = "";

      // Check if Time Settings have been submitted.
      if(isset($_POST["submit_time"]))
      {
         for($i = 0; $i < count($timeCmds); $i++)
         {
            $cmdStr = $timeCmds[$i];
            $pyArgsStr = $pyArgsStr." --".$cmdStr." '".$_POST[$cmdStr."_val"]."'";
         }
      }

      // Check if Smart Plug Settings have been submitted.
      if(isset($_POST["submit_smart_plug"]))
      {
         for($i = 0; $i < count($switchCmds); $i++)
         {
            $cmdStr = $switchCmds[$i];
            $pyArgsStr = $pyArgsStr." --".$cmdStr." '".$_POST[$cmdStr."_val"]."'";
         }
      }

      // Check if Valid Temperature Settings have been submitted.
      if(isset($_POST["submit_valid_temp"]))
      {
         for($i = 0; $i < count($validTempCmds); $i++)
         {
            $cmdStr = $validTempCmds[$i];
            $pyArgsStr = $pyArgsStr." --".$cmdStr." '".$_POST[$cmdStr."_val"]."'";
         }
      }

      // Set / Get (if a button was pressed, $pyArgsStr will be filled in with the set info).
      setGet($pyArgsStr);
      if($pyArgsStr != "")
      {
         header("Location: #");
      }

      function getSwitchStateAfter_dropdown()
      {
          global $SwitchStateAfterTimeOfDayStop;
          $selectedVal = $SwitchStateAfterTimeOfDayStop;
          $validOptions = array('Off', 'On', 'No Change');

          # Generate the dropdown HTML code, making sure the current value is at the top (there is probably a better way to do this).
          $dropDownHtml = "<option value=".$selectedVal.">".$selectedVal."</option>";
          for($i = 0; $i < count($validOptions); $i++)
          {
             $optStr = $validOptions[$i];
             if($optStr != $selectedVal)
             {
               $dropDownHtml = $dropDownHtml."<option value=".$optStr.">".$optStr."</option>";
             }
          }
          return $dropDownHtml;
      }
   ?>
   
   <div class="navbar">
      <a href="status.php">Status</a>
      <a href="basic.php">Settings</a>
      <a href="graph.php">Graph</a>
      <a href="log.php">Log</a>
   </div>
   <div class="settingsnavbar">
      <a href="basic.php">Basic</a>
      <a href="advanced.php">Advanced</a>
   </div>
   <br><br><br><br><br>

   <center>
      <form action="advanced.php" method="post">

         <h1>Time Settings</h1>
         <table cellpadding="5">
            <tr>
               <td>Time Between Temp Checks</td>
               <td><input name="TimeBetweenTempCheck_val" type="number" value="<?php echo $TimeBetweenTempCheck;?>" /></td>
               <td>seconds</td>
            </tr>
            <tr>
               <td colspan="3"><center><input name="submit_time" type="submit" value="Update Time Settings" /></center></td>
            </tr>
         </table>
         <br><hr>

         <h1>Smart Plug Settings</h1>
         <table cellpadding="5">
            <tr>
               <td>Smart Plug IP</td>
               <td colspan="2"><input name="SmartPlugIpAddr_val" type="text" value="<?php echo $SmartPlugIpAddr;?>" /></td>
            </tr>
            <tr>
               <td>Min Switch Toggle Time</td>
               <td><input name="MinTimeBetweenChangingSwitchState_val" type="number" value="<?php echo $MinTimeBetweenChangingSwitchState;?>" /></td>
               <td>seconds</td>
            </tr>
            <tr>
               <td>Min Switch Retry Time</td>
               <td><input name="MinTimeBetweenRetryingSwitchChange_val" type="number" value="<?php echo $MinTimeBetweenRetryingSwitchChange;?>" /></td>
               <td>seconds</td>
            </tr>
            <tr>
               <td>Switch State After Control Time</td>
               <td colspan="2">
                  <select name="SwitchStateAfterTimeOfDayStop_val">
                     <?php echo getSwitchStateAfter_dropdown();?>
                  </select>
               </td>
            </tr>
            <tr>
               <td colspan="3"><center><input name="submit_smart_plug" type="submit" value="Update Smart Plug Settings" /></center></td>
            </tr>
         </table>
         <br><hr>

         <h1>Valid Temperature Range</h1>
         <table cellpadding="5">
            <tr>
               <td>Min Valid Temp</td>
               <td width="1"><input name="InvalidTempLow_val" type="number" value="<?php echo $InvalidTempLow;?>" /></td>
               <td>°F</td>
            </tr>
            <tr>
               <td>Max Valid Temp</td>
               <td width="1"><input name="InvalidTempHigh_val" type="number" value="<?php echo $InvalidTempHigh;?>" /></td>
               <td>°F</td>
            </tr>
            <tr>
               <td colspan="3"><center><input name="submit_valid_temp" type="submit" value="Update Valid Temp Settings" /></center></td>
            </tr>
         </table>
         <br>

      </form>

   </center>
   </body>
</html>