<?php
   // Get the current settings.
   include 'setGetSettings.php';
   setGet("");
?>

<html>
<head>
<link rel="stylesheet" type="text/css" href="thermo.css">
<meta name="viewport" content="width=device-width" />
<style>
</style>
<title><?php echo $DeviceName;?></title>
<link rel="icon" href="<?php echo $hotColdIconImgIcon;?>">
</head>
   <body style='background-color : <?php echo $DeviceColor;?>' >
   
   <?php
      /////////////////////////////////////////////////////////
      // This code will run every time something happens.
      /////////////////////////////////////////////////////////
      //
      $basicCmds = array(
         'TimeOfDayToStart',
         'TimeOfDayToStop',
         'SwitchOnTemp',
         'SwitchOffTemp'
      );

      $pyArgsStr = "";

      // Check if the button was pressed.
      if(isset($_POST["submit_basic"]))
      {
         for($i = 0; $i < count($basicCmds); $i++)
         {
            $cmdStr = $basicCmds[$i];
            $pyArgsStr = $pyArgsStr." --".$cmdStr." '".$_POST[$cmdStr."_val"]."'";
         }
      }

      // Set / Get (if a button was pressed, $pyArgsStr will be filled in with the set info).
      setGet($pyArgsStr);
      if($pyArgsStr != "")
      {
         header("Location: #");
      }

   ?>
       
   <div class="devicebar">
      <table style="width:100%"><tr>
         <td><?php echo $DeviceName;?></td>
         <td><img src="<?php echo $hotColdIconImg17;?>"> <?php echo $currentTemperature;?></td>
      </tr></table>
   </div>
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
   <br><br><br><br><br><br><br><br>

   <center>
      <h1>Basic Settings</h1>
      <form action="basic.php" method="post">
         <table cellpadding="5">
            <tr>
               <td>Start Time</td>
               <td colspan="2"><input name="TimeOfDayToStart_val" type="time" value="<?php echo $TimeOfDayToStart;?>" /></td>
            </tr>
            <tr>
               <td>Stop Time</td>
               <td colspan="2"><input name="TimeOfDayToStop_val" type="time" value="<?php echo $TimeOfDayToStop;?>" /></td>
            </tr>
            <tr>
               <td>On Temp</td>
               <td width="1"><input name="SwitchOnTemp_val" type="number" value="<?php echo $SwitchOnTemp;?>" /></td>
               <td>°F</td>
            </tr>
            <tr>
               <td>Off Temp</td>
               <td width="1"><input name="SwitchOffTemp_val" type="number" value="<?php echo $SwitchOffTemp;?>" /></td>
               <td>°F</td>
            </tr>
            <tr>
               <td colspan="3"><center><input name="submit_basic" type="submit" value="Update Basic Settings" /></center></td>
            </tr>
         </table>

         <br><img src="<?php echo $hotColdIconImg48;?>">
      </form>

   </center>
   </body>
</html>