<?php
   // Get the current settings.
   include 'setGetSettings.php';
   setGet("");
?>

<html>
<head>
<link rel="stylesheet" type="text/css" href="thermo.css">
<meta name="viewport" content="width=device-width" />
<title><?php echo $DeviceName;?></title>
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
   <br><br><br><br><br>

   <center>
      <h1>Log</h1>
      <form action="log.php" method="post">
      <textarea rows="80" cols="60"><?php echo file_get_contents("tempCtrlSwitch.log"); ?></textarea>
      </form>
   </center>
   </body>
</html>