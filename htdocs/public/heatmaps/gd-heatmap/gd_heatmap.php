<?php

/**
 * A class for generating heatmaps using the GD image library.
 *
 * http://blog.ampli.fi/heatmap-generation-library-using-php-and-gd/
 *
 * TODO Automatic generation of gradient from source or from scratch.
 *
 */
Class gd_heatmap {
  private $config;
  private $debug_log;
  private $im;

  /**
   * @param array $data
   *   An array containing the data to be represented by the heatmap. Each
   *   element is a non-associative array with three values, where the first one
   *   is the x-coordinate, second the y-coordinate and third the value in that
   *   coordinate.
   *
   * @param array $config
   *   An array containing configuration variables:
   *   debug - Set to TRUE to print out debug data in the image.
   *   r - radius of each data point.
   *   width - width of the image.
   *   height - height of the image.
   *   noc - Number of colours to be used in the heatmap. More colours looks
   *     nicer but is heavier to process.
   *   dither - Boolean. Dithered images tend to look better than non-dithered
   *     if noc is about less than 16.
   *   format - String, "png" or "jpeg"
   *   fill_with_smallest - Boolean. If set to true, the image won't be filled
   *     (i.e. areas with 0 value won't be coloured) with white/transparent,
   *     but instead with a colour that matches the gradient's low end.
   */
  function __construct($data, $config = array()) {
    $default_config = array(
      'debug' => FALSE,
      'r' => 50,
      'width' => 640,
      'height' => 480,
      'noc' => 16,
      'dither' => FALSE,
      'format' => 'png',
      'fill_with_smallest' => false,
    );
    
    foreach ($default_config as $key => $value) {
      if (isset($config[$key])) {
        $this->config[$key] = $config[$key];
      }
      else {
        $this->config[$key] = $default_config[$key];      
      }
    }
    
    if ($this->config['format'] != 'png' && $this->config['format'] != 'jpeg') {
      $this->error('Invalid format "' . $this->config['format'] . '". Supported formats include png and jpeg.');
    }
    
    $this->debug_log = '';
    
    $this->generate_image($data);
  }
  
  /**
   * @param string $key
   *   The configuration option to get.
   *
   * @return mixed
   *   The value of the configuration option.
   */
  public function get_config($key) {
    return $this->config[$key];
  }
  
  
  /**
   * Generates the actual heatmap.
   */
  private function generate_image($data) {
    require_once('gd-rg.php');
    $time = microtime(1); $this->logg('Started at ' . $time);
    
    // Find the maximum value from the given data.
    $max_data_value = 1;
    foreach ($data as $row) {
      if (isset($row[2]) && $max_data_value < $row[2]) {
        $max_data_value = $row[2];
      }
    }
    $this->logg('Done sorting data at ' . (microtime(1) - $time));
    
    // Create the heatmap image.
    $im = imagecreatetruecolor($this->get_config('width'), $this->get_config('height'));
    $white = imagecolorallocate($im, 255, 255, 255);
    imagefill($im, 0, 0, $white);
    imagealphablending($im, true);
    imagesavealpha($im, true);
    
    // Create a separate spot image for each value to be shown, with different
    // amounts of black. Having 25 separate shades of colour looks like a decent
    // number.
    $spots = array();
    for ($i = 0; $i < $this->config['noc']; $i++) {
      // The gradient lib doesn't like too small values for $alpha_end, so we use
      // $noc for that, which happens to work well.
      $alpha_end = $this->map($i, 0, $this->config['noc'] - 1, $this->config['noc'], 255);
      $temp = new gd_gradient_alpha($this->config['r'], $this->config['r'], 'ellipse','#000', 0x00, $alpha_end, 0);
      $spot = $temp->get_image();
      imagealphablending($spot, true);
      imagesavealpha($spot, true);
      $spots[$i] = $spot;
    }
    $this->logg('Created '.count($spots).' spots at ' . (microtime(1) - $time));

    // Go through the data, and add appropriate spot images to the heatmap
    // image.
    for ($i = 0; $i < count($data); $i++) {
      $value = (isset($data[$i][2]) ? $data[$i][2] : 1);
      $value = $this->map($value, 1, $max_data_value, 0, $this->config['noc'] - 1);
      imagecopy($im , $spots[$value], $data[$i][0], $data[$i][1] , 0 , 0 , $this->config['r'] , $this->config['r']);
    }
    $this->logg('Copied spots to image at ' . (microtime(1) - $time));

    imagetruecolortopalette($im, $this->config['dither'], $this->config['noc']);
    $this->logg('Flattened black at ' . (microtime(1) - $time));

    // Get the gradient from an image file
    // FIX: Fetch image in current __FILE__ directory (script including this might be somewhere else)
    $gi = dirname(__FILE__) . '/gradient-' . $this->config['noc'] . ($this->config['fill_with_smallest'] ? "-fill" : "") . '.png';
    if (!file_exists($gi)) {
      $this->error("Can't find gradient file " . $gi . ". Make one using gradient-source.jpg");
    }
    $gs = imagecreatefrompng($gi);
    imagetruecolortopalette($gs, TRUE, $this->config['noc']);

    // Get a list of different gray values in the image, and order them.
    $grays = array();
    $imagecolorstotal = imagecolorstotal($im);
    // FIX: Loop over all colors supported by gradient instead of colors in image (might not contain all)
    for ($i = 0; $i < $this->config['noc']; $i++) {
      if ($i >= $imagecolorstotal) {
        $c = array('red'=> 0, 'green'=> 0, 'blue'=> 0);
      } else {
        $c = imagecolorsforindex($im, $i);
      }
      $grays[] = str_pad(($c['red'] * 65536) + ($c['green'] * 256) + $c['blue'], 8, '0', STR_PAD_LEFT) . ':' . $i;
    }
    sort($grays);
    $indexes = array();
    foreach ($grays as $gray) {
      $indexes[] = substr($gray, strpos($gray, ':') + 1);
    }
    $this->logg('Created gray indexes at ' . (microtime(1) - $time));

    // Replace each shade of gray with the matching rainbow colour.
    $i = 0;
    foreach ($indexes as $index) {
      $fill_index = imagecolorat($gs , $i, 0);
      $fill_color = imagecolorsforindex($gs, $fill_index);
      imagecolorset($im, $index, $fill_color['red'], $fill_color['green'], $fill_color['blue']);
      $i++;
    }

    $this->logg('Replaced black with rainbow at ' . (microtime(1) - $time));

    if (!$this->config['fill_with_smallest']) {
      // Finally switch from white background to transparent.
      $closest = imagecolorclosest ($im, 255 , 255 , 255);
      imagecolortransparent($im, $closest);
      $this->logg('Made transparent at ' . (microtime(1) - $time));
    }

    $this->logg('done at ' . (microtime(1) - $time));
    
    // Debugging text
    if ($this->config['debug']) {
      $text_color = imagecolorallocate($im, 0, 0, 0);
      $y = 5;
      foreach (explode("\n", $this->debug_log) as $line) {
        imagestring($im, 3, 250, $y, $line, $text_color);
        $y = $y + 10;
      }    
    }
    $this->im = $im;
  }

  /**
   * Prints out an error in the image if something went horribly wrong.
   */  
  function error ($text) {
    $im = imagecreate(600, 480);
    $bg_color = imagecolorallocate($im, 255, 0, 0);
    $text_color = imagecolorallocate($im, 0, 0, 0);
    imagestring($im, 3, 5, 5, $text , $text_color);
    header('Content-type: image/png');
    imagepng($im);
    imagedestroy($im);
    die();
  }
  
  /**
   * @return Object The generated GD image object containing the heatmap.
   */
  public function get_image() {
    return $this->im;
  }
  
  /**
   * Prints out the generated image or saves it into a file.
   */
  public function output($filename = null) {
    if (!$filename) {
      header('Content-type: image/' . $this->config['format']);
    }
    switch ($this->config['format']) {
      case 'png':
        imagepng($this->im, $filename);
        break;
      case 'jpeg':
        imagejpeg($this->im, $filename);
        break;
    }
    imagedestroy($this->im);
  }
  
  /**
   * Debugging function.
   */
  private function logg($thing) {
    if (!$this->config['debug']) {
      return;
    }
    if (is_array($thing) || is_object($thing)) {
      $out = print_r($thing, 1);
    }
    else {
      $out = $thing;
    }
    $this->debug_log .= $out . "\n";
  }
  
  /**
   * Simple utility function for mapping values from one range to another.
   * Copied from http://stackoverflow.com/questions/7742959/php-map-a-value-using-fromrange-and-torange
   *
   */
  private function map($value, $fromLow, $fromHigh, $toLow, $toHigh) {
      $fromRange = $fromHigh - $fromLow;
      $toRange = $toHigh - $toLow;
      $scaleFactor = $toRange / $fromRange;
      $tmpValue = $value - $fromLow;
      $tmpValue *= $scaleFactor;
      return $tmpValue + $toLow;
  }
  
  function debug() {
    echo $this->debug_log;
  }
  
  /**
   * @param integer $w
   *   The maximum x-coordinate of the test points.
   * @param integer $h
   *   The maximum y-coordinate of the test points.
   *   height.
   * @param integer $r
   *   The radius of a single data point. Used to calculate data point distance
   *   from image edges.
   * @param integer $n
   *   The number of data points generated.
   * @param integer $mv
   *   The maximum value of a single data point.
   *
   * @return array Test data that can be passed to the heatmap constructor.
   */
  public static function get_test_data($w, $h, $r, $n = 200, $mv = 1500) {
    $data = array();

    for ($i = 0; $i < $n; $i++) {
      $x = rand(0 - $r, $w );
      $y = rand(0 - $r, $h );
      $v = rand(1, $mv);

      $data[] = array($x, $y, $v);
    }

    return $data;
  }
}
