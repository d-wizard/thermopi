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
    
    <?php
        /////////////////////////////////////////////////////////
        // This code will run every time something happens.
        /////////////////////////////////////////////////////////        
        $pythonScript = "python ".$thermoPythonDir."getTempChartArray.py";
        $titleStr = "'Temperature - 1 Day'";

        $time = 3600*24;
        $numPoints = 600;

        if(isset($_GET["submit_1hr"]))
        {
          $time = 3600;
          $numPoints = 100;
          $titleStr = "'Temperature - 1 Hr'";
        }
        if(isset($_GET["submit_4hr"]))
        {
          $time = 3600*4;
          $numPoints = 400;
          $titleStr = "'Temperature - 4 Hrs'";
        }
        if(isset($_GET["submit_12hr"]))
        {
          $time = 3600*12;
          $numPoints = 500;
          $titleStr = "'Temperature - 12 Hrs'";
        }
        if(isset($_GET["submit_1day"]))
        {
          $time = 3600*24;
          $numPoints = 600;
          $titleStr = "'Temperature - 1 Day'";
        }
        if(isset($_GET["submit_3day"]))
        {
          $time = 3600*24*3;
          $numPoints = 800;
          $titleStr = "'Temperature - 3 Days'";
        }
        if(isset($_GET["submit_7day"]))
        {
          $time = 3600*24*7;
          $numPoints = 2000;
          $titleStr = "'Temperature - 7 Days'";
        }
    ?>
    <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
    <script type="text/javascript">
      google.charts.load('current', {'packages':['corechart']});
      google.charts.setOnLoadCallback(drawChart);

      var chartW = window.innerWidth;
      var chartH = window.innerHeight;

      var upperH = Math.floor(chartW/1.1);
      var lowerH = 200;
      chartH = chartH - 100;


      if (chartH > upperH) {
        chartH = upperH;
      }
      if (chartH < lowerH) {
        chartH = lowerH;
      }

      function drawChart() {
        var data = google.visualization.arrayToDataTable([
          [{type: 'datetime', label: 'Time'}, 'Switch State', 'Temperature (°F)'],
          <?php echo shell_exec($pythonScript." -t ".$time." -n ".$numPoints);?>
        ]);

        var options = {
          title: <?php echo $titleStr;?>,
          titleTextStyle: { fontSize: 20},
          legend: { position: 'bottom' },
          // Gives each series an axis that matches the vAxes number below.
          series: {
            0: {targetAxisIndex: 1, color: '#F06846'},
            1: {targetAxisIndex: 0, color: '#3366CC'}
          },
          vAxes: {
            // Adds titles to each axis.
            1: {ticks: [0,1], textPosition: 'none'},
            0: {title: 'Temperature (°F)', textPosition: 'out'}
          },
          backgroundColor: '<?php echo $DeviceColor;?>',
          width: chartW,
          height: chartH
        };

        var chart = new google.visualization.LineChart(document.getElementById('curve_chart_with_switch'));

        chart.draw(data, options);
      }
    </script>
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
   <br><br>
   <br><br>
   <br><br>
    <center>
    <form action="graph.php" method="get">
      <input name="submit_1hr" type="submit" value="1 Hr" />
      <input name="submit_4hr" type="submit" value="4 Hr" />
      <input name="submit_12hr" type="submit" value="12 Hr" />
      <input name="submit_1day" type="submit" value="1 Day" />
      <input name="submit_3day" type="submit" value="3 Day" />
      <input name="submit_7day" type="submit" value="7 Day" />
    </form>
    <div id="curve_chart_with_switch"></div>
    </center>
  </body>
</html>