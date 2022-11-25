<?php
  // Get the current settings.
  $thisScriptDir = dirname(__FILE__);
  $thermoPythonDir = $thisScriptDir."/../"; # The directory with all the python scripts is up one directory from this script.
?>

<html>
  <head>
    <link rel="stylesheet" type="text/css" href="thermo.css">
    <meta name="viewport" content="width=device-width" />
    
    <?php
        /////////////////////////////////////////////////////////
        // This code will run every time something happens.
        /////////////////////////////////////////////////////////
        $topics = array(
          'xxx/xxx/xxxxx',
          'yyy/yyy/yyyyy'
        );
        $topic = $topics[0]; // Default to first in array.

        $pythonScript = "python3 ".$thermoPythonDir."getTempChartArray.py";
        $titleStr = "1 Day";

        $time = 3600*24;
        $numPoints = 600;
        $updateButtonSubmitName  = "update_topic";

        if(isset($_GET["submit_1hr"]))
        {
          $time = 3600;
          $numPoints = 100;
          $titleStr = "1 Hr";
          $updateButtonSubmitName = "submit_1hr";
        }
        if(isset($_GET["submit_4hr"]))
        {
          $time = 3600*4;
          $numPoints = 400;
          $titleStr = "4 Hrs";
          $updateButtonSubmitName = "submit_4hr";
        }
        if(isset($_GET["submit_12hr"]))
        {
          $time = 3600*12;
          $numPoints = 500;
          $titleStr = "12 Hrs";
          $updateButtonSubmitName = "submit_12hr";
        }
        if(isset($_GET["submit_1day"]))
        {
          $time = 3600*24;
          $numPoints = 600;
          $titleStr = "1 Day";
          $updateButtonSubmitName = "submit_1day";
        }
        if(isset($_GET["submit_3day"]))
        {
          $time = 3600*24*3;
          $numPoints = 800;
          $titleStr = "3 Days";
          $updateButtonSubmitName = "submit_3day";
        }
        if(isset($_GET["submit_7day"]))
        {
          $time = 3600*24*7;
          $numPoints = 2000;
          $titleStr = "7 Days";
          $updateButtonSubmitName = "submit_7day";
        }
        if(isset($_GET["submit_30day"]))
        {
          $time = 3600*24*30;
          $numPoints = 3000;
          $titleStr = "30 Days";
          $updateButtonSubmitName = "submit_30day";
        }

        if(isset($_GET["Topic"]))
        {
          $topic = $_GET['Topic'];
        }

        $recentTempInfo = shell_exec($pythonScript." -t ".$topic." -r");
        $recentTempInfo_arr = explode ("|", $recentTempInfo);
        $recentTime = $recentTempInfo_arr[0];
        $recentTemp = $recentTempInfo_arr[1]." °F";

        function getTopicDropdownHtml()
        {
            global $topics;
            global $topic;
            $selectedVal = $topic;

            # Generate the dropdown HTML code, making sure the current value is at the top (there is probably a better way to do this).
            $dropDownHtml = "<option value=".$selectedVal.">".$selectedVal."</option>";
            for($i = 0; $i < count($topics); $i++)
            {
              $optStr = $topics[$i];
              if($optStr != $selectedVal)
              {
                $dropDownHtml = $dropDownHtml."<option value=".$optStr.">".$optStr."</option>";
              }
            }
            return $dropDownHtml;
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
      chartH = chartH - 200;


      if (chartH > upperH) {
        chartH = upperH;
      }
      if (chartH < lowerH) {
        chartH = lowerH;
      }

      function drawChart() {
        var data = google.visualization.arrayToDataTable([
          [{type: 'datetime', label: 'Time'}, 'Temperature (°F)'],
          <?php echo shell_exec($pythonScript." -c ".$time." -n ".$numPoints." -t ".$topic);?>
        ]);

        var options = {
          chartArea:{
            left:"12%",
            right:"4%",
            bottom:"12%",
            top:"4%",
            width:"95%",
            height:"90%"
          },
          titleTextStyle: { fontSize: 20},
          legend: { position: 'bottom' },
          // Gives each series an axis that matches the vAxes number below.
          series: {
            0: {targetAxisIndex: 0, color: '#3366CC'}
          },
          vAxes: {
            // Adds titles to each axis.
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
    <title><?php echo "Topic: ".$topic;?></title>
  </head>
   <body style='background-color : <?php echo $DeviceColor;?>' >
   <div class="devicebar">
      <table style="width:100%"><tr>
         <td><?php echo $recentTime;?></td>
         <td><?php echo $recentTemp;?></td>
      </tr></table>
   </div>
   <br><br><br>
    <center>

    <h3><?php echo "Topic: ".$topic." - ".$titleStr;?></h3>
    <form action="graph.php" method="get">
      <select name="Topic">
        <?php echo getTopicDropdownHtml();?>
      </select>
      <input name=<?php echo $updateButtonSubmitName;?> type="submit" value="Update" />
      <br>
      <br>
      <input name="submit_1hr" type="submit" value="1 Hr" />
      <input name="submit_4hr" type="submit" value="4 Hr" />
      <input name="submit_1day" type="submit" value="1 Day" />
      <input name="submit_3day" type="submit" value="3 Day" />
      <input name="submit_7day" type="submit" value="7 Day" />
      <input name="submit_30day" type="submit" value="30 Day" />
    </form>
    <div id="curve_chart_with_switch"></div>
    </center>
  </body>
</html>