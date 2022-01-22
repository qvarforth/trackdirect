<?php
header('Access-Control-Allow-Origin: *');
header("Cache-Control: max-age=2592000"); //30days (60sec * 60min * 24hours * 30days)


// Contains ascii values that corresponds to symbols with overlay support (for symbols in the alternative table)
$alternativeSymbolWithOverlaySupport = [33, 35, 37, 38, 39, 45, 62, 64, 79, 87, 91, 95, 97, 115, 122, 48, 65, 68, 69, 72, 94, 99, 105, 110,  117, 118];

$alternativeSymbolThatShouldNotBeFlipped = [115, 62, 94, 79];
$primarySymbolThatShouldNotBeFlipped = [94, 83, 39, 88];

$primarySymbolRotateDiff[40] = -90;
$primarySymbolRotateDiff[42] = -90;
$primarySymbolRotateDiff[60] = -90;
$primarySymbolRotateDiff[61] = -90;
$primarySymbolRotateDiff[62] = -90;
$primarySymbolRotateDiff[67] = -90;
$primarySymbolRotateDiff[70] = -90;
$primarySymbolRotateDiff[80] = -90;
$primarySymbolRotateDiff[85] = -90;
$primarySymbolRotateDiff[89] = -90;
$primarySymbolRotateDiff[91] = -90;
$primarySymbolRotateDiff[97] = -90;
$primarySymbolRotateDiff[98] = -90;
$primarySymbolRotateDiff[101] = -90;
$primarySymbolRotateDiff[102] = -90;
$primarySymbolRotateDiff[103] = -90;
$primarySymbolRotateDiff[106] = -90;
$primarySymbolRotateDiff[107] = -90;
$primarySymbolRotateDiff[115] = -90;
$primarySymbolRotateDiff[117] = -90;
$primarySymbolRotateDiff[118] = -90;

$primarySymbolRotateDiff[39] = 0; // Small Airplace
$primarySymbolRotateDiff[94] = 0; // Large Airplane
$primarySymbolRotateDiff[83] = 0;
$primarySymbolRotateDiff[88] = 0; // Helicopter

$alternativeSymbolRotateDiff[106] = -90;
$alternativeSymbolRotateDiff[107] = -90;
$alternativeSymbolRotateDiff[117] = -90;
$alternativeSymbolRotateDiff[115] = 0;
$alternativeSymbolRotateDiff[118] = -90;
$alternativeSymbolRotateDiff[91] = -90;
$alternativeSymbolRotateDiff[94] = 0;
$alternativeSymbolRotateDiff[79] = 0;
$alternativeSymbolRotateDiff[62] = 0;

$svgContent = null;
if (isset($_GET['symbol']) && isset($_GET['symbol_table'])) {

    // symbol and symbol_table is ascii values so everything should be numbers
    $symbol = preg_replace("/[^0-9]/","",$_GET['symbol']);
    $symbolTable = preg_replace("/[^0-9]/","",$_GET['symbol_table']);

    if ($symbol >= 32 && $symbol <= 126) {

        // Init $course
        if (isset($_GET['course'])) {
            $course = preg_replace("/[^0-9]/","",$_GET['course']);
            while ($course > 360) {
                $course = $course - 360;
            }
            while ($course < 0) {
                $course = $course + 360;
            }
            if ($course == 360) {
                $course = 0;
            }
        } else {
            $course = null;
        }

        // Init hight and width
        if (isset($_GET['width']) && isset($_GET['height'])) {
            $width = preg_replace("/[^0-9]/","",$_GET['width']);
            $height = preg_replace("/[^0-9]/","",$_GET['height']);

            if ($width > 1024) {
                $width = 1024;
            }

            if ($height > 1024) {
                $height = 1024;
            }
        } else {
            $width = null;
            $height = null;
        }

        // Init scale hight and width
        if (isset($_GET['scale_width']) && isset($_GET['scale_height'])) {
            $scaleWidth = preg_replace("/[^0-9]/","",$_GET['scale_width']);
            $scaleHeight = preg_replace("/[^0-9]/","",$_GET['scale_height']);

            if ($scaleWidth > 1024) {
                $scaleWidth = 1024;
            }

            if ($scaleHeight > 1024) {
                $scaleHeight = 1024;
            }

            if ($scaleWidth == 24 && $scaleHeight == 24) {
                $scaleWidth = null;
                $scaleHeight = null;
            }
        } else {
            $scaleWidth = null;
            $scaleHeight = null;
        }

        // Init $symbolCategory and $overlay
        $overlay = null;
        if ($symbolTable == 47) {
            // Primary table (47 == '/')
            $symbolCategory = 1;

        } else if ($symbolTable == 92) {
            // Alternative table (92 == '\')
            $symbolCategory = 2;

        } else if (preg_match("/^[a-zA-Z\d]$/", chr($symbolTable))) {
            // Alternative table with overlay

            $filepath1 = './svgicons/' . $symbol . '-' . $symbolTable . '.svg';
            $filepath2 = './svgicons/' . $symbol . '-' . '3.svg';
            if (file_exists($filepath1)) {
                $symbolCategory = $symbolTable;
            } else if (file_exists($filepath2)) {
                $symbolCategory = 3;
            } else {
                $symbolCategory = 2;
            }

            if (in_array($symbol, $alternativeSymbolWithOverlaySupport) && ($symbolCategory == 2 || $symbolCategory == 3)) {
                $overlay = chr($symbolTable);
            }

        } else {
            // Use primary if nothing else fits
            $symbolCategory = 1;
        }

        // Init $filepath
        $name = $symbol . '-' . $symbolCategory;
        $filepath = './svgicons/' . $name . '.svg';

        if (file_exists($filepath)) {
            $svgContent = file_get_contents($filepath);

            if ($overlay !== null || $course !== null || ($width !== null && $height !== null) || ($scaleWidth !== null && $scaleHeight !== null)) {

                // We will do changes to symbol (course or overlay)

                $doc = new DOMDocument();
                $doc->loadXML($svgContent);
                $svg = $doc->getElementsByTagName('svg')->item(0);

                $childs = Array();
                foreach ($svg->childNodes as $child) {
                    if (isset($child->tagName) && $child->tagName != 'metadata') {
                        $childs[] = $child;
                    }
                }

                // Wrapper1 used for width and height transfrom
                $wrapper1 = $doc->createElement('g');
                $wrapper1 = $svg->appendChild($wrapper1);

                // Wrapper 2 used for rotate
                $wrapper2 = $doc->createElement('g');
                $wrapper2 = $wrapper1->appendChild($wrapper2);

                // Wrapper 3 used for flip
                $wrapper3 = $doc->createElement('g');
                $wrapper3 = $wrapper2->appendChild($wrapper3);

                // Wrapper 4 used for text
                $wrapper4 = $doc->createElement('g');
                $wrapper4 = $wrapper3->appendChild($wrapper4);

                foreach ($childs as $child) {
                    $removedChild = $svg->removeChild($child);
                    $wrapper4->appendChild($child);
                }

                if ($overlay !== null) {
                    // We should add overlay
                    // dominant-baseline do not seem to be supported by internet explorer so we have to do vertical alignment manual by changing y

                    $text = $doc->createElement('text');
                    $text->setAttribute('id','textoverlay');
                    $text = $wrapper4->appendChild($text);

                    $tspan = $doc->createElement('tspan', chr($symbolTable));
                    $tspan = $text->appendChild($tspan);

                    $tspan->setAttribute('id','tspanoverlay');
                    //$tspan->setAttribute('sodipodi:linespacing','0%');
                    $tspan->setAttribute('font-family','Helvetica');
                    $tspan->setAttribute('text-anchor','middle');
                    $tspan->setAttribute('text-align','center');
                    $tspan->setAttribute('word-spacing','0');
                    //$tspan->setAttribute('line-height','0%');
                    $tspan->setAttribute('letter-spacing','0');
                    $tspan->setAttribute('font-weight','bold');
                    $tspan->setAttribute('x','12'); // left/right (higher means more to the right)
                    $tspan->setAttribute('y','12'); // up/down (higher means more down)


                    // White text, normal size, bold, centered
                    if (in_array($symbol, Array(35, 38, 62, 87, 95, 97))) {
                        $tspan->setAttribute('fill','#ffffff');
                        $tspan->setAttribute('font-size','14');
                        $tspan->setAttribute('dy','5.2');
                        $tspan->setAttribute('dx','0');

                        if (in_array(chr($symbolTable), array('Y', 'V'))) {
                            $tspan->setAttribute('dx','-0.2');
                        }

                        if (in_array(chr($symbolTable), array('S', 'W', 'Q'))) {
                            $tspan->setAttribute('dx','-0.1');
                        }

                        if (in_array(chr($symbolTable), array('R', 'P', 'D', 'F', 'K', 'L'))) {
                            $tspan->setAttribute('dx','0.4');
                        }
                    }

                    // White text, normal size, bold, centered (little bit to the left)
                    if (in_array($symbol, Array(105))) {
                        $tspan->setAttribute('fill','#ffffff');
                        $tspan->setAttribute('font-size','14');
                        $tspan->setAttribute('dy','4.5');
                        $tspan->setAttribute('dx','-0.5');

                        if (in_array(chr($symbolTable), array('S', 'W'))) {
                            $tspan->setAttribute('dx','-0.6');
                        }

                        if (in_array(chr($symbolTable), array('R', 'P', 'D', 'F', 'K', 'L'))) {
                            $tspan->setAttribute('dx','-0.1');
                        }
                    }

                    // White/Yellow text, normal size, bold, centered, a bit lower
                    if (in_array($symbol, Array(37, 110, 115, 122))) {
                        if ($symbol == 37) {
                            $tspan->setAttribute('fill','#ffff00');
                        } else {
                            $tspan->setAttribute('fill','#ffffff');
                        }
                        $tspan->setAttribute('font-size','14');
                        $tspan->setAttribute('dy','8');
                        $tspan->setAttribute('dx','-0.1');

                        if (in_array(chr($symbolTable), array('T'))) {
                            $tspan->setAttribute('dx','0');
                        }

                        if (in_array(chr($symbolTable), array('S', 'Y'))) {
                            $tspan->setAttribute('dx','-0.2');
                        }
                    }

                    // Black text, normal size, bold, centered, a bit lower
                    if (in_array($symbol, Array(45))) {
                        $tspan->setAttribute('fill','#000000');
                        $tspan->setAttribute('font-size','14');
                        $tspan->setAttribute('dy','8');
                        $tspan->setAttribute('dx','-0.1');

                        if (in_array(chr($symbolTable), array('S', 'Y'))) {
                            $tspan->setAttribute('dx','-0.2');
                        }
                    }

                    // White text, normal size, bold, centered
                    if (in_array($symbol, Array(68, 69))) {
                        $tspan->setAttribute('fill','#ffffff');
                        $tspan->setAttribute('font-size','14');
                        $tspan->setAttribute('dy','4.6');

                        if (in_array(chr($symbolTable), array('R', 'P', 'D', 'F', 'K', 'L'))) {
                            $tspan->setAttribute('dx','0.4');
                        }


                        if (in_array(chr($symbolTable), array('S', 'Y'))) {
                            $tspan->setAttribute('dx','-0.2');
                        }
                    }

                    // Black text, normal size, bold, centered
                    if (in_array($symbol, Array(48, 65, 72))) {
                        $tspan->setAttribute('fill','#000000');
                        $tspan->setAttribute('font-size','14');
                        $tspan->setAttribute('dy','4.6');

                        if (in_array(chr($symbolTable), array('R', 'P', 'D', 'F', 'K', 'L'))) {
                            $tspan->setAttribute('dx','0.4');
                        }
                    }

                    // Black text, normal size, bold, centered, a bit higher
                    if (in_array($symbol, Array(79))) {
                        $tspan->setAttribute('fill','#000000');
                        $tspan->setAttribute('font-size','14');
                        $tspan->setAttribute('dy','1.5');

                        if (in_array(chr($symbolTable), array('R', 'P', 'D', 'F', 'K', 'L'))) {
                            $tspan->setAttribute('dx','0.4');
                        }
                    }

                    // Black text, smaller size, bold, centered
                    if (in_array($symbol, Array(99))) {
                        $tspan->setAttribute('fill','#000000');
                        $tspan->setAttribute('font-size','12');
                        $tspan->setAttribute('dy','5');

                        if (in_array(chr($symbolTable), array('S', 'W'))) {
                            $tspan->setAttribute('dx','-0.1');
                        }
                    }

                    // Black text, very very small size, bold, right upper corner (besides airplane, human, symbol)
                    if (in_array($symbol, Array(33, 39, 91, 94))) {
                        $tspan->setAttribute('fill','#000000');
                        $tspan->setAttribute('font-size','9');
                        if ($symbol == 39 || $symbol == 33) {
                            $tspan->setAttribute('dx','17');
                        } else {
                            $tspan->setAttribute('dx','11');
                        }
                        $tspan->setAttribute('dy','-4');
                    }

                    // White text, small size, bold, centered, a bit lower
                    if (in_array($symbol, Array(64))) {
                        $tspan->setAttribute('fill','#ffffff');
                        $tspan->setAttribute('font-size','10');
                        $tspan->setAttribute('dy','3.4');
                        $tspan->setAttribute('dx','-0.1');
                    }

                    // White text, very small size, bold, a bit to the right (on trucks)
                    if (in_array($symbol, Array(117))) {
                        $tspan->setAttribute('fill','#ffffff');
                        $tspan->setAttribute('font-size','9');
                        $tspan->setAttribute('dy','0.7');
                        $tspan->setAttribute('dx','-3');
                    }

                    // White text, very small size, bold, a bit to the right (on vans)
                    if (in_array($symbol, Array(118))) {
                        $tspan->setAttribute('fill','#ffffff');
                        $tspan->setAttribute('font-size','9');
                        $tspan->setAttribute('dy','0.3');
                        $tspan->setAttribute('dx','-3');
                    }
                }


                if ($course !== null) {
                    // We should rotate symbol
                    if ($symbolCategory == 1 && isset($primarySymbolRotateDiff[$symbol])) {
                        $adjustedCourse = $course + $primarySymbolRotateDiff[$symbol];
                    } else if ($symbolCategory != 1 && isset($alternativeSymbolRotateDiff[$symbol])) {
                        $adjustedCourse = $course + $alternativeSymbolRotateDiff[$symbol];
                    } else {
                        $course = 0;
                        $adjustedCourse = 0;
                    }

                    $wrapper2->setAttribute('transform', 'rotate(' . $adjustedCourse . ' 12 12)');
                    if (($symbolCategory == 1 && !in_array($symbol, $primarySymbolThatShouldNotBeFlipped))
                        || ($symbolCategory != 1 && !in_array($symbol, $alternativeSymbolThatShouldNotBeFlipped))) {

                        if ($course > 180) {
                            // Symbols that rotate more than 180 deg should be flipped
                            $wrapper3->setAttribute('transform', 'translate(0,24) scale(1, -1)');

                            if (isset($tspan)) {
                                // Flip letter back
                                $x = 24 + $tspan->getAttribute('dx');
                                $tspan->setAttribute('transform', 'translate(' . $x . ', 0) scale(-1, 1)');
                            }

                        }
                    }
                }

                if ($width !== null && $height !== null) {
                    // We should change svg size (not scaling!), center existing stuff
                    $wrapper1->setAttribute('transform', 'translate('.(($width-24)/2).' '.(($height-24)/2).')');
                    $svg->setAttribute('viewBox', '0 0 '.$width.' '.$height);
                    $svg->setAttribute('width', $width);
                    $svg->setAttribute('height', $height);
                }

                if ($scaleWidth !== null && $scaleHeight !== null) {
                    $svg->setAttribute('preserveAspectRatio',"xMinYMin meet");
                    if ($width !== null && $height !== null) {
                        $svg->setAttribute('viewBox', '0 0 '.$width.' '.$height);
                    } else {
                        $svg->setAttribute('viewBox', "0 0 24 24");
                    }
                    $svg->setAttribute('width', $scaleWidth);
                    $svg->setAttribute('height', $scaleHeight);
                }

                $svgContent = $doc->saveXML();
            }
        }
    }
}

if ($svgContent === null) {
    $filepath = './svgicons/125-1.svg';
    $svgContent = file_get_contents($filepath);
}

if (isset($_GET['format']) && $_GET['format'] == 'png') {
    str_replace('#000000', '#010101', $svgContent);

    $im = new Imagick();

    // Hack to set needed density to get correct size?!
    if ($width !== null && $height !== null) {
        $im->setResolution($width*4,$height*4);
    } else {
        $im->setResolution(96,96);
    }

    $im->setBackgroundColor(new ImagickPixel('transparent'));
    $im->readImageBlob($svgContent);
    $im->setImageFormat("png32");

    if ((!isset($scaleWidth) && !isset($scaleHeight)) || ($scaleWidth == null && $scaleHeight == null)
            || ($scaleWidth == 24 && $scaleHeight == 24)
            || ($scaleWidth == 64 && $scaleHeight == 64)
            || ($scaleWidth == 150 && $scaleHeight == 150)) {
        $im->writeImage('./' . basename($_SERVER['REQUEST_URI']));
    }

    header('Pragma: public');
    header('Cache-Control: max-age=86400, public');
    header('Expires: '. gmdate('D, d M Y H:i:s \G\M\T', time() + 86400));
    header('Content-type: image/png');
    echo $im->getImageBlob();

    $im->destroy();

} else {

    header('Pragma: public');
    header('Cache-Control: max-age=86400, public');
    header('Expires: '. gmdate('D, d M Y H:i:s \G\M\T', time() + 86400));
    header('Content-type: image/svg+xml');
    echo $svgContent;
}
