<?php
   // Get the current settings.
   include 'setGetSettings.php';
   setGet("");
?>

<html>
<head>
<link rel="stylesheet" type="text/css" href="thermo.css">
<meta name="viewport" content="width=device-width" />
<title>Basic Settings</title>
</head>
   <body style='background-color : <?php echo $DeviceColor;?>' >
      
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
   <br><br><br><br><br><br>

   <center>
      <table cellpadding="5">
         <tr>
            <td colspan="3"><div class="statusName">Temperature</div></td>
         </tr>
         <tr>
            <td></td><td></td><!-- Poor man's indent. -->
            <td><div class="statusVal"><?php echo $currentTemperature;?></div></td>
         </tr>
      </table>
      <br>
      <table cellpadding="5">
         <tr>
            <td colspan="3"><div class="statusName">Switch State</div></td>
         </tr>
         <tr>
            <td></td><td></td><!-- Poor man's indent. -->
            <td><div class="statusVal"><?php echo $switchState;?></div></td>
         </tr>
      </table>
      <br><br><img src="<?php echo $hotColdIconImg;?>">
   </center>

   </body>
</html>