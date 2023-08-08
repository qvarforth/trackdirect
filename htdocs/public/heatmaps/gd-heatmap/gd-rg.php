<?php

/**
 * This class is originally from here: http://planetozh.com/download/gd-gradient-fill.php
 *
 * It was then modified by StackOverflow user Justin (http://stackoverflow.com/users/265575/justin)
 * ..in this question: http://stackoverflow.com/questions/6615602/radial-gradients-with-opacity-in-php
 * ..to support alpha, and uploaded here: http://codepad.org/1eZ3Km0J/fork .
 * 
 * Only a couple of changes were needed to use this class with the heatmap lib.
 *
 */
class gd_gradient_alpha {
    public $image;
    public $width;
    public $height;
    public $direction;
    public $alphastart;
    public $alphaend;
    public $step;
    public $color;

    // Constructor. Creates, fills and returns an image
    function __construct($w,$h,$d,$rgb,$as,$ae,$step=0) {
        $this->width = $w;
        $this->height = $h;
        $this->direction = $d;
        $this->color = $rgb;
        $this->alphastart = $as;
        $this->alphaend = $ae;
        $this->step = intval(abs($step));

        // Attempt to create a blank image in true colors, or a new palette based image if this fails
        if (function_exists('imagecreatetruecolor')) {
            $this->image = imagecreatetruecolor($this->width,$this->height);
        } elseif (function_exists('imagecreate')) {
            $this->image = imagecreate($this->width,$this->height);
        } else {
            die('Unable to create an image');
        }

        imagealphablending($this->image, false);
        imagesavealpha($this->image, true);

        // Fill it
        $this->fillalpha($this->image,$this->direction,$this->color,$this->alphastart,$this->alphaend);

        // Show it
        //$this->display($this->image);

        // Return it
        //return $this->image;
    }
 
    function get_image() {
        return $this->image;
    }


    // Displays the image with a portable function that works with any file type
    // depending on your server software configuration
    function display ($im) {
        if (function_exists("imagepng")) {
            header("Content-type: image/png");
            imagepng($im);
        }
        elseif (function_exists("imagegif")) {
            header("Content-type: image/gif");
            imagegif($im);
        }
        elseif (function_exists("imagejpeg")) {
            header("Content-type: image/jpeg");
            imagejpeg($im, "", 0.5);
        }
        elseif (function_exists("imagewbmp")) {
            header("Content-type: image/vnd.wap.wbmp");
            imagewbmp($im);
        } else {
            die("Doh ! No graphical functions on this server ?");
        }
        return true;
    }


    // The main function that draws the gradient
    function fillalpha($im,$direction,$rgb,$as,$ae) {

        list($r,$g,$b) = $this->hex2rgb($rgb);
        $a1 = $this->a2sevenbit($as);
        $a2 = $this->a2sevenbit($ae);

        switch($direction) {
            case 'horizontal':
                $line_numbers = imagesx($im);
                $line_width = imagesy($im);
                break;
            case 'vertical':
                $line_numbers = imagesy($im);
                $line_width = imagesx($im);
                break;
            case 'ellipse':
                $width = imagesx($im);
                $height = imagesy($im);
                $rh=$height>$width?1:$width/$height;
                $rw=$width>$height?1:$height/$width;
                $line_numbers = min($width,$height);
                $center_x = $width/2;
                $center_y = $height/2;
                imagefill($im, 0, 0, imagecolorallocatealpha($im, $r, $g, $b, $a1));
                break;
            case 'ellipse2':
                $width = imagesx($im);
                $height = imagesy($im);
                $rh=$height>$width?1:$width/$height;
                $rw=$width>$height?1:$height/$width;
                $line_numbers = sqrt(pow($width,2)+pow($height,2));
                $center_x = $width/2;
                $center_y = $height/2;
                break;
            case 'circle':
                $width = imagesx($im);
                $height = imagesy($im);
                $line_numbers = sqrt(pow($width,2)+pow($height,2));
                $center_x = $width/2;
                $center_y = $height/2;
                $rh = $rw = 1;
                break;
            case 'circle2':
                $width = imagesx($im);
                $height = imagesy($im);
                $line_numbers = min($width,$height);
                $center_x = $width/2;
                $center_y = $height/2;
                $rh = $rw = 1;
                imagefill($im, 0, 0, imagecolorallocatealpha($im, $r, $g, $b, $a1));
                break;
            case 'square':
            case 'rectangle':
                $width = imagesx($im);
                $height = imagesy($im);
                $line_numbers = max($width,$height)/2;
                break;
            case 'diamond':
                $width = imagesx($im);
                $height = imagesy($im);
                $rh=$height>$width?1:$width/$height;
                $rw=$width>$height?1:$height/$width;
                $line_numbers = min($width,$height);
                break;
            default:
        }

        for ( $i = 0; $i < $line_numbers; $i=$i+1+$this->step ) {
            $old_a = ( empty($a) ) ? $a2 : $a;
            $a = ( $a2 - $a1 != 0 ) ? intval( $a1 + ( $a2 - $a1 ) * ( $i / $line_numbers ) ): $a1;

            if ( "$old_a" != "$a") {
                $fill = imagecolorallocatealpha( $im, $r, $g, $b, $a );
            }
            switch($direction) {
                case 'vertical':
                    imagefilledrectangle($im, 0, $i, $line_width, $i+$this->step, $fill);
                    break;
                case 'horizontal':
                    imagefilledrectangle( $im, $i, 0, $i+$this->step, $line_width, $fill );
                    break;
                case 'ellipse':
                case 'ellipse2':
                case 'circle':
                case 'circle2':
                    imagefilledellipse ($im,$center_x, $center_y, ($line_numbers-$i)*$rh, ($line_numbers-$i)*$rw,$fill);
                    break;
                case 'square':
                case 'rectangle':
                    imagefilledrectangle ($im,$i*$width/$height,$i*$height/$width,$width-($i*$width/$height), $height-($i*$height/$width),$fill);
                    break;
                case 'diamond':
                    imagefilledpolygon($im, array (
                        $width/2, $i*$rw-0.5*$height,
                        $i*$rh-0.5*$width, $height/2,
                        $width/2,1.5*$height-$i*$rw,
                        1.5*$width-$i*$rh, $height/2 ), 4, $fill);
                    break;
                default:
            }
        }
    }

    // #ff00ff -> array(255,0,255) or #f0f -> array(255,0,255)
    function hex2rgb($color) {
        $color = str_replace('#','',$color);
        $s = strlen($color) / 3;
        $rgb[]=hexdec(str_repeat(substr($color,0,$s),2/$s));
        $rgb[]=hexdec(str_repeat(substr($color,$s,$s),2/$s));
        $rgb[]=hexdec(str_repeat(substr($color,2*$s,$s),2/$s));
        return $rgb;
    }

    function a2sevenbit($alpha) {
        return (abs($alpha - 255) >> 1);
    }

}
