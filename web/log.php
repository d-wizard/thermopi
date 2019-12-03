<html>
<head>
<link rel="stylesheet" type="text/css" href="thermo.css">
<meta name="viewport" content="width=device-width" />
<title>Log</title>
</head>
   <body>
   
   <div class="navbar">
      <a href="status.php">Status</a>
      <a href="basic.php">Settings</a>
      <a href="graph.php">Graph</a>
      <a href="log.php">Log</a>
   </div>
   <br><br>

   <center>
      <h1>Log</h1>
      <form action="log.php" method="post">
      <textarea rows="80" cols="60"><?php echo file_get_contents("tempCtrlSwitch.log"); ?></textarea>
      </form>
   </center>
   </body>
</html>