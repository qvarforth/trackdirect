<?php
// This is a test script demonstrating the use of the gd-heatmap library.
require_once('gd_heatmap.php');

// Generate some test data using the static function provided for that purpose.
$data = gd_heatmap::get_test_data(1240, 600, 50, 500);

// Config array with all the available options. See the constructor's doc block
// for explanations.
$config = array(
  'debug' => TRUE,
  'width' => 1240,
  'height' => 600,
  'noc' => 32,
  'r' => 50,
  'dither' => FALSE,
  'format' => 'jpeg',
  'fill_with_smallest' => false,
);

// Create a new heatmap based on the data and the config.
$heatmap = new gd_heatmap($data, $config);

// And print it out. If you're having trouble getting any images out of the
// library , comment this out to allow your browser to show you the error
// messages.
$heatmap->output();

// Or save it to a file. Don't forget to set correct file permissions in the
// target directory.
//$heatmap->output('savetest.png');
