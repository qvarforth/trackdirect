<?php

/**
 * Returnes true if user probably prefer Imperial Units
 *
 * @return boolean
 */
function isImperialUnitUser()
{
    if (isset($_GET['imperialUnits']) && $_GET['imperialUnits']) {
        return true;
    } else if (isset($_GET['imperialUnits']) && !$_GET['imperialUnits']) {
        return false;
    }

    if (isset($_SERVER['HTTP_ACCEPT_LANGUAGE'])) {

        if (substr($_SERVER['HTTP_ACCEPT_LANGUAGE'], 0, 5) == 'en-US') {
            // USA
            return true;
        }

        if (substr($_SERVER['HTTP_ACCEPT_LANGUAGE'], 0, 2) == 'my') {
            // Myanmar / Burma
            return true;
        }

        if (substr($_SERVER['HTTP_ACCEPT_LANGUAGE'], 0, 5) == 'en-LR') {
            // Liberia
            return true;
        }
    }

    return false;
}

/**
 * Convert km to miles (or kmh to mph)
 *
 * @param  {float} value
 * @return float
 */
function convertKilometerToMile($value)
{
    return $value * 0.621371192;
}

/**
 * Convert meter to feet
 *
 * @param  {float} value
 * @return float
 */
function convertMeterToFeet($value)
{
    return $value * 3.2808399;
}

/**
 * Convert meter per second to miles per second
 *
 * @param  {float} value
 * @return float
 */
function convertMpsToMph($value)
{
    return $value * 2.23693629;
}

/**
 * Convert meter to yard
 *
 * @param  {float} value
 * @return float
 */
function convertMeterToYard($value)
{
    return $value * 1.0936133;
}

/**
 * Convert mm to inches
 *
 * @param  {float} value
 * @return float
 */
function convertMmToInch($value)
{
    return $value * 0.0393700787;
}

/**
 * Convert celcius to fahrenheit
 *
 * @param  {float} value
 * @return float
 */
function convertCelciusToFahrenheit($value)
{
    return $value * (9/5) + 32;
}

/**
 * Convert hPa/mbar to mmhg
 *
 * @param  {float} value
 * @return float
 */
function convertMbarToMmhg($value)
{
    return $value * 0.75006375541921;
}

/**
 * Returnes true if value is float
 *
 * @param  mixed $value
 * @return boolean
 */
function isFloat($value)
{
    if (is_numeric($value)) {
        // PHP automagically tries to coerce $value to a number
        return is_float($value + 0);
    }
    return false;
}

/**
 * Returnes true if value is int
 *
 * @param  mixed $value
 * @return boolean
 */
function isInt($value)
{
    return (ctype_digit(strval($value)));
}

/**
 * Replace first occurence
 *
 * @param  string $search
 * @param  string $replace
 * @param  string $string
 * @return string
 */
function str_replace_first($search, $replace, $string)
{
    $pos = strpos($string, $search);
    if ($pos !== false) {
        return substr_replace($string, $replace, $pos, strlen($search));
    } else {
        return $string;
    }
}

/*
 * Returnes symbol description
 *
 * @param string $symbolTable
 * @param string $symbol
 * @param boolean $includeUndefinedOverlay
 * @return string
 */
function getSymbolDescription($symbolTable, $symbol, $includeUndefinedOverlay)
{
    if ($symbolTable == '/') {
        switch ($symbol) {
        case '!':
            return 'Police, Sheriff';
        case '"':
            return 'No Symbol';
        case '#':
            return 'Digipeater';
        case '$':
            return 'Phone';
        case '%':
            return 'DX Cluster';
        case '&':
            return 'HF Gateway';
        case '\'':
            return 'Small Aircraft';
        case '(':
            return 'Mobile Satellite Station';
        case ')':
            return 'Wheelchair (handicapped)';
        case '*':
            return 'Snowmobile';
        case '+':
            return 'Red Cross';
        case ',':
            return 'Scout (Boy Scout)';
        case '-':
            return 'House (VHF)';
        case '.':
            return 'X';
        case '/':
            return 'Red Dot';
        case '0':
            return 'Circle (0)';
        case '1':
            return 'Circle (1)';
        case '2':
            return 'Circle (2)';
        case '3':
            return 'Circle (3)';
        case '4':
            return 'Circle (4)';
        case '5':
            return 'Circle (5)';
        case '6':
            return 'Circle (6)';
        case '7':
            return 'Circle (7)';
        case '8':
            return 'Circle (8)';
        case '9':
            return 'Circle (9)';
        case ':':
            return 'Fire';
        case ';':
            return 'Campground or Portable operation';
        case '<':
            return 'Motorcycle';
        case '=':
            return 'Railroad Engine';
        case '>':
            return 'Car';
        case '?':
            return 'File server';
        case '@':
            return 'Hurricane prediction';
        case 'A':
            return 'Aid Station';
        case 'B':
            return 'BBS or PBBS';
        case 'C':
            return 'Canoe';
        case 'D':
            return 'No Symbol'; // was originally undefined
        case 'E':
            return 'Event (Special live event)'; // Eyeball
        case 'F':
            return 'Farm Vehicle (tractor)';
        case 'G':
            return 'Grid Square (6 digit)';
        case 'H':
            return 'Hotel (blue bed symbol)';
        case 'I':
            return 'TCP/IP network station';
        case 'J':
            return 'No Symbol';
        case 'K':
            return 'School';
        case 'L':
            return 'Logged-ON user (or PC User)';
        case 'M':
            return 'MacAPRS';
        case 'N':
            return 'NTS Station';
        case 'O':
            return 'Balloon';
        case 'P':
            return 'Police';
        case 'Q':
            return 'TBD';
        case 'R':
            return 'Recreational Vehicle';
        case 'S':
            return 'Shuttle';
        case 'T':
            return 'SSTV';
        case 'U':
            return 'Bus';
        case 'V':
            return 'ATV';
        case 'W':
            return 'National Weather Service';
        case 'X':
            return 'Helicopter';
        case 'Y':
            return 'Yacht (sail)';
        case 'Z':
            return 'WinAPRS';
        case '[':
            return 'Human/Person';
        case '\\':
            return 'Triangle (DF station)';
        case ']':
            return 'Mail/PostOffice';
        case '^':
            return 'Large Aircraft';
        case '_':
            return 'Weather Station';
        case '`':
            return 'Dish Antenna';
        case 'a':
            return 'Ambulance';
        case 'b':
            return 'Bike';
        case 'c':
            return 'Incident Command Post';
        case 'd':
            return 'Fire Station';
        case 'e':
            return 'Horse (equestrian)';
        case 'f':
            return 'Fire Truck';
        case 'g':
            return 'Glider';
        case 'h':
            return 'Hospital';
        case 'i':
            return 'IOTA (islands on the air)';
        case 'j':
            return 'Jeep';
        case 'k':
            return 'Truck';
        case 'l':
            return 'Laptop';
        case 'm':
            return 'Mic-E Repeater';
        case 'n':
            return 'Node (black bulls-eye)';
        case 'o':
            return 'EOC';
        case 'p':
            return 'Rover (puppy, or dog)';
        case 'q':
            return 'Grid square';
        case 'r':
            return 'Antenna';
        case 's':
            return 'Power Boat';
        case 't':
            return 'Truck Stop';
        case 'u':
            return 'Truck (18 wheeler)';
        case 'v':
            return 'Van';
        case 'w':
            return 'Water Station';
        case 'x':
            return 'xAPRS (Unix)';
        case 'y':
            return 'Yagi @ QTH';
        case 'z':
            return 'Shelter';
        case '{':
            return 'No Symbol';
        case '|':
            return 'TNC Stream Switch';
        case '}':
            return 'No Symbol';
        case '~':
            return 'TNC Stream Switch';
        }

    } else {
        switch ($symbol) {
        case '!':
            switch ($symbolTable) {
            case "\\":
                return 'Emergency!';
            case 'E':
                return 'ELT or EPIRB';
            case 'V':
                return 'Volcanic Eruption or Lava';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Emergency (with overlay ' . $symbolTable . ')';
                } else {
                    return null;
                }
            }

        case '"':
            switch ($symbolTable) {
            case "\\":
                return 'No Symbol';
            default:
                if ($includeUndefinedOverlay) {
                    return 'No Symbol';
                } else {
                    return null;
                }
            }

        case '#':
            switch ($symbolTable) {
            case '\\':
                return 'Digipeater';
            case 'A':
                return 'Digipeater (An Alt-Freq input digi)';
            case 'R':
                return 'Digipeater (RELAY only)';
            case 'W':
                return 'Digipeater (RELAY and WIDE)';
            case 'T':
                return 'Digipeater (PacComm RELAY,WIDE and TRACE)';
            case 'N':
                return 'Digipeater (WIDEn-N and relay,wide,trace)';
            case 'I':
                return 'Digipeater (digipeater is also an IGate)';
            case 'L':
                return 'Digipeater (LIMITED New n-N Paradigm digi)';
            case 'S':
                return 'Digipeater (New n-N Paradigm digi)';
            case 'P':
                return 'Digipeater (PacComm, New n-N Paradigm)';
            case 'U':
                return 'Digipeater (UI-DIGI firmware)';
            case 'D':
                return 'Digipeater (DIGI_NED)';
            case '1':
                return 'Digipeater (Fill-in digi, 1-hop limit)';
            case 'X':
                return 'Digipeater (Experimental)';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Digipeater (with overlay ' . $symbolTable . ')';
                } else {
                    return null;
                }
            }

        case '$':
            switch ($symbolTable) {
            case '\\':
                return 'Bank or ATM';
            case 'U':
                return 'ATM (US dollars)';
            case 'L':
                return 'ATM (Brittish Pound)';
            case 'Y':
                return 'ATM (Japanese Yen)';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Bank or ATM (with overlay ' . $symbolTable . ')';
                } else {
                    return null;
                }
            }
        case '%':
            switch ($symbolTable) {
            case '\\':
                return 'Power/Energy';
            case 'C':
                return 'Power/Energy (Coal)';
            case 'E':
                return 'Power/Energy (Emergency)';
            case 'G':
                return 'Power/Energy (Geothermal)';
            case 'H':
                return 'Power/Energy (Hydroelectric)';
            case 'N':
                return 'Power/Energy (Nuclear)';
            case 'P':
                return 'Power/Energy (Portable)';
            case 'S':
                return 'Power/Energy (Solar)';
            case 'T':
                return 'Power/Energy (Turbine)';
            case 'W':
                return 'Power/Energy (Wind)';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Power/Energy';
                } else {
                    return null;
                }
            }
        case '&':
            switch ($symbolTable) {
            case '\\':
                return 'Gateway';
            case 'I':
                return 'Igate (Generic)';
            case 'R':
                return 'Receive only IGate';
            case 'P':
                return 'PSKmail node';
            case 'T':
                return 'TX Igate (with path set to 1 hop)';
            case 'W':
                return 'WIRES-X';
            case '2':
                return 'TX igate (with path set to 2 hops)';
            case 'D':
                return 'D-STAR (D-PRS IGate)';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Gateway (with overlay ' . $symbolTable . ')';
                } else {
                    return null;
                }
            }

        case '\'':
            switch ($symbolTable) {
            case '\\':
                return 'Incident site (Airplane Crash Site)';
            case 'A':
                return 'Incident site (Automobile crash site)';
            case 'H':
                return 'Incident site (Hazardous incident)';
            case 'M':
                return 'Incident site (Multi-Vehicle crash site)';
            case 'P':
                return 'Incident site (Pileup)';
            case 'T':
                return 'Incident site (Truck wreck)';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Incident site';
                } else {
                    return null;
                }
            }
        case '(':
            switch ($symbolTable) {
            case "\\":
                return 'Cloudy';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Cloudy';
                } else {
                    return null;
                }
            }

        case ')':
            switch ($symbolTable) {
            case "\\":
                return 'Firenet MEO (Modis Earth Observatory)';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Firenet MEO (Modis Earth Observatory)';
                } else {
                    return null;
                }
            }

        case '*':
            switch ($symbolTable) {
            case "\\":
                return 'Snow';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Snow';
                } else {
                    return null;
                }
            }

        case '+':
            switch ($symbolTable) {
            case "\\":
                return 'Church';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Church';
                } else {
                    return null;
                }
            }

        case ',':
            switch ($symbolTable) {
            case "\\":
                return 'Scout (Girl Scout)';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Scout (Girl Scout)';
                } else {
                    return null;
                }
            }

        case '-':
            switch ($symbolTable) {
            case '\\':
                return 'House (HF)';
            case '5':
                return 'House (50 Hz mains power)';
            case '6':
                return 'House (60 Hz mains power)';
            case 'B':
                return 'House (Backup Battery Power)';
            case 'C':
                return 'House (Ham club)';
            case 'E':
                return 'House (Emergency power)';
            case 'G':
                return 'House (Geothermal)';
            case 'H':
                return 'House (Hydro powered)';
            case 'O':
                return 'House (Operator Present)';
            case 'S':
                return 'House (Solar Powered)';
            case 'W':
                return 'House (Wind powered)';
            default:
                if ($includeUndefinedOverlay) {
                    return 'House (with overlay ' . $symbolTable . ')';
                } else {
                    return null;
                }
            }
        case '.':
            switch ($symbolTable) {
            case "\\":
                return 'Unknown Position';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Unknown Position';
                } else {
                    return null;
                }
            }

        case '/':
            switch ($symbolTable) {
            case "\\":
                return 'Waypoint Destination';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Waypoint Destination';
                } else {
                    return null;
                }
            }

        case '0':
            switch ($symbolTable) {
            case '\\':
                return 'Circle';
            case 'A':
                return 'Allstar Node';
            case 'E':
                return 'Echolink Node';
            case 'I':
                return 'IRLP repeater';
            case 'S':
                return 'Staging Area';
            case 'V':
                return 'Echolink and IRLP (VOIP)';
            case 'W':
                return 'WIRES (Yaesu VOIP)';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Circle (with overlay ' . $symbolTable . ')';
                } else {
                    return null;
                }
            }

        case '1':
        case '2':
        case '3':
        case '4':
        case '5':
        case '6':
        case '7':
            switch ($symbolTable) {
            case "\\":
                return 'No Symbol';
            default:
                if ($includeUndefinedOverlay) {
                    return 'No Symbol';
                } else {
                    return null;
                }
            }

        case '8':
            switch ($symbolTable) {
            case '\\':
                return 'No Symbol';
            case '8':
                return '802.11 network node';
            case 'G':
                return '802.11G';
            default:
                if ($includeUndefinedOverlay) {
                    return 'No Symbol';
                } else {
                    return null;
                }
            }

        case '9':
            switch ($symbolTable) {
            case "\\":
                return 'Gas Station';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Gas Station';
                } else {
                    return null;
                }
            }

        case ':':
            switch ($symbolTable) {
            case "\\":
                return 'Hail (weather condition)';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Hail (weather condition)';
                } else {
                    return null;
                }
            }

        case ';':
            switch ($symbolTable) {
            case '\\':
                return 'Portable, Park or Picnic';
            case 'F':
                return 'Field Day';
            case 'I':
                return 'Islands on the air';
            case 'S':
                return 'Summits on the air';
            case 'W':
                return 'WOTA';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Portable';
                } else {
                    return null;
                }
            }

        case '<':
            switch ($symbolTable) {
            case "\\":
                return 'Advisory (single gale flag)';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Advisory (single gale flag)';
                } else {
                    return null;
                }
            }

        case '=':
            switch ($symbolTable) {
            case "\\":
                return 'No Symbol';
            default:
                if ($includeUndefinedOverlay) {
                    return 'No Symbol';
                } else {
                    return null;
                }
            }

        case '>':
            switch ($symbolTable) {
            case '\\':
                return 'Car';
            case '1':
            case '2':
            case '3':
            case '4':
            case '5':
            case '6':
            case '7':
            case '8':
            case '9':
            case '0':
                return 'Numbered Car (' . $symbolTable . ')';
            case 'E':
                return 'Car (Electric)';
            case 'H':
                return 'Car (Hybrid)';
            case 'S':
                return 'Car (Solar powered)';
            case 'V':
                return 'Car (GM Volt)';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Car (with overlay ' . $symbolTable . ')';
                } else {
                    return null;
                }
            }
        case '?':
            switch ($symbolTable) {
            case "\\":
                return 'Info Kiosk';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Info Kiosk';
                } else {
                    return null;
                }
            }

        case '@':
            switch ($symbolTable) {
            case "\\":
                return 'Hurricane/Tropical storm';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Hurricane/Tropical storm (with overlay ' . $symbolTable . ')';
                } else {
                    return null;
                }
            }

        case 'A':
            switch ($symbolTable) {
            case '\\':
                return 'Box';
            case '9':
                return 'Mobile DTMF user';
            case '7':
                return 'HT DTMF user';
            case 'H':
                return 'House DTMF user';
            case 'E':
                return 'Echolink DTMF report';
            case 'I':
                return 'IRLP DTMF report';
            case 'R':
                return 'RFID report';
            case 'A':
                return 'AllStar DTMF report';
            case 'D':
                return 'D-Star report';
            case 'X':
                return 'OLPC Laptop XO';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Box (' . $symbolTable . ')';
                } else {
                    return null;
                }
            }
        case 'B':
            switch ($symbolTable) {
            case "\\":
                return 'Blowing snow';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Blowing snow';
                } else {
                    return null;
                }
            }

        case 'C':
            switch ($symbolTable) {
            case "\\":
                return 'Coast Guard';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Coast Guard';
                } else {
                    return null;
                }
            }

        case 'D':
            switch ($symbolTable) {
            case '\\':
                return 'Depot'; // drizzle rain moved to ' ovlyD
            case 'A':
                return 'Airport';
            case 'F':
                return 'Ferry Landing';
            case 'H':
                return 'Heloport';
            case 'R':
                return 'Rail Depot';
            case 'B':
                return 'Bus Depot';
            case 'L':
                return 'LIght Rail or Subway';
            case 'S':
                return 'Seaport Depot';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Depot (with overlay ' . $symbolTable . ')';
                } else {
                    return null;
                }
            }
        case 'E':
            switch ($symbolTable) {
            case '\\':
                return 'Smoke';
            case 'H':
                return 'Haze';
            case 'S':
                return 'Smoke';
            case 'B':
                return 'Blowing Snow'; // was \B
            case 'D':
                return 'Blowing Dust or Sand'; // was \b
            case 'F':
                return 'Fog'; // was \{
            default:
                if ($includeUndefinedOverlay) {
                    return 'Smoke (with overlay ' . $symbolTable . ')';
                } else {
                    return null;
                }
            }
        case 'F':
            switch ($symbolTable) {
            case "\\":
                return 'Freezing rain';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Freezing rain';
                } else {
                    return null;
                }
            }

        case 'G':
            switch ($symbolTable) {
            case "\\":
                return 'Snow Shower';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Snow Shower';
                } else {
                    return null;
                }
            }

        case 'H':
            switch ($symbolTable) {
            case '\\':
                return 'Haze';
            case 'R':
                return 'Radiation detector';
            case 'W':
                return 'Hazardous Waste';
            case 'X':
                return 'Skull&Crossbones';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Hazard (with overlay ' . $symbolTable . ')';
                } else {
                    return null;
                }
            }
        case 'I':
            switch ($symbolTable) {
            case "\\":
                return 'Rain Shower';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Rain Shower';
                } else {
                    return null;
                }
            }

        case 'J':
            switch ($symbolTable) {
            case "\\":
                return 'Lightning';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Lightning';
                } else {
                    return null;
                }
            }

        case 'K':
            switch ($symbolTable) {
            case "\\":
                return 'Kenwood HT';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Kenwood HT';
                } else {
                    return null;
                }
            }

        case 'L':
            switch ($symbolTable) {
            case "\\":
                return 'Lighthouse';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Lighthouse (with overlay ' . $symbolTable . ')';
                } else {
                    return null;
                }
            }

        case 'M':
            switch ($symbolTable) {
            case "\\":
                return 'No Symbol';
            default:
                if ($includeUndefinedOverlay) {
                    return 'No Symbol';
                } else {
                    return null;
                }
            }

        case 'N':
            switch ($symbolTable) {
            case "\\":
                return 'Navigation Buoy';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Navigation Buoy (with overlay ' . $symbolTable . ')';
                } else {
                    return null;
                }
            }

        case 'O':
            switch ($symbolTable) {
            case '\\':
                return 'Rocket (amateur)';
            case 'B':
                return 'Blimp (non-rigid airship)';
            case 'M':
                return 'Manned Balloon';
            case 'T':
                return 'Teathered Balloon';
            case 'C':
                return 'Constant Pressure Balloon - Long duration';
            case 'R':
                return 'Rocket bearing Balloon (Rockoon)';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Balloon (with overlay ' . $symbolTable . ')';
                } else {
                    return null;
                }
            }
        case 'P':
            switch ($symbolTable) {
            case "\\":
                return 'Parking';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Parking (with overlay ' . $symbolTable . ')';
                } else {
                    return null;
                }
            }

        case 'Q':
            switch ($symbolTable) {
            case "\\":
                return 'Quake';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Quake';
                } else {
                    return null;
                }
            }

        case 'R':
            switch ($symbolTable) {
            case '\\':
                return 'Restaurant (generic)';
            case '7':
                return 'Restaurant (7/11)';
            case 'K':
                return 'Restaurant (KFC)';
            case 'M':
                return 'Restaurant (McDonalds)';
            case 'T':
                return 'Restaurant (Taco Bell)';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Restaurant (with overlay ' . $symbolTable . ')';
                } else {
                    return null;
                }
            }
        case 'S':
            switch ($symbolTable) {
            case "\\":
                return 'Satellite/Pacsat';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Satellite/Pacsat (with overlay ' . $symbolTable . ')';
                } else {
                    return null;
                }
            }

        case 'T':
            switch ($symbolTable) {
            case "\\":
                return 'Thunderstorm';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Thunderstorm (with overlay ' . $symbolTable . ')';
                } else {
                    return null;
                }
            }

        case 'U':
            switch ($symbolTable) {
            case "\\":
                return 'Sunny';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Sunny (with overlay ' . $symbolTable . ')';
                } else {
                    return null;
                }
            }

        case 'V':
            switch ($symbolTable) {
            case "\\":
                return 'VORTAC Navigation Aid';
            default:
                if ($includeUndefinedOverlay) {
                    return 'VORTAC Navigation Aid';
                } else {
                    return null;
                }
            }

        case 'W':
            switch ($symbolTable) {
            case "\\":
                return 'National Weather Service';
            default:
                if ($includeUndefinedOverlay) {
                    return 'National Weather Service (with overlay ' . $symbolTable . ')';
                } else {
                    return null;
                }
            }

        case 'X':
            switch ($symbolTable) {
            case "\\":
                return 'Pharmacy';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Pharmacy';
                } else {
                    return null;
                }
            }

        case 'Y':
            switch ($symbolTable) {
            case '\\':
                return 'Radio/APRS Device';
            case 'A':
                return 'Alinco';
            case 'B':
                return 'Byonics';
            case 'I':
                return 'Icom';
            case 'K':
                return 'Kenwood';
            case 'Y':
                return 'Yaesu/Standard';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Radio/APRS Device'; // or "No Symbol"?
                } else {
                    return null;
                }
            }
        case 'Z':
            switch ($symbolTable) {
            case "\\":
                return 'No Symbol';
            default:
                if ($includeUndefinedOverlay) {
                    return 'No Symbol';
                } else {
                    return null;
                }
            }

        case '[':
            switch ($symbolTable) {
            case '\\':
                return 'Wall Cloud (or pedestal cloud)';
            case 'B':
                return 'Baby on board (stroller, pram etc)';
            case 'S':
                return 'Skier';
            case 'R':
                return 'Runner';
            case 'H':
                return 'Hiker';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Human/Person (with overlay ' . $symbolTable . ')';
                } else {
                    return null;
                }
            }

        case '\\':
            switch ($symbolTable) {
            case '\\':
                return 'No Symbol';
            case 'A':
                return 'Avmap G5';
            default:
                if ($includeUndefinedOverlay) {
                    return 'No Symbol';
                } else {
                    return null;
                }
            }
        case ']':
            switch ($symbolTable) {
            case "\\":
                return 'No Symbol';
            default:
                if ($includeUndefinedOverlay) {
                    return 'No Symbol';
                } else {
                    return null;
                }
            }

        case '^':
            switch ($symbolTable) {
            case '\\':
                return 'Aircraft'; // top-view originally intended to point in direction of flight
            case 'A':
                return 'Aircraft (A = Autonomous)';
            case 'D':
                return 'Aircraft (D = Drone)';
            case 'E':
                return 'Aircraft (E = Electric aircraft)';
            case 'G':
                return 'Aircraft (G = Glider aircraft)';
            case 'H':
                return 'Aircraft (H = Hovercraft)';
            case 'J':
                return 'Aircraft (J = JET)';
	    case 'L':
                return 'Paraglider'; // Not official definition
            case 'M':
                return 'Aircraft (M = Missle)';
            case 'P':
                return 'Aircraft (P = Propeller)';
            case 'R':
                return 'Aircraft (R = Remotely Piloted)';
            case 'S':
                return 'Aircraft (S = Solar Powered)';
            case 'V':
                return 'Aircraft (V = Vertical takeoff)';
            case 'X':
                return 'Aircraft (X = Experimental)';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Aircraft (with overlay ' . $symbolTable . ')';
                } else {
                    return null;
                }
            }

        case '_':
            switch ($symbolTable) {
            case "\\":
                return 'Weather Station';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Weather Station (with overlay ' . $symbolTable . ')';
                } else {
                    return null;
                }
            }

        case '`':
            switch ($symbolTable) {
            case "\\":
                return 'Rain';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Rain';
                } else {
                    return null;
                }
            }

        case 'a':
            switch ($symbolTable) {
            case '\\':
                return 'Red Diamond';
            case 'A':
                return 'ARES';
            case 'D':
                return 'D-STAR (previously Dutch ARES)';
            case 'G':
                return 'RSGB Radio Society of Great Brittan';
            case 'R':
                return 'RACES';
            case 'S':
                return 'SATERN Salvation Army';
            case 'W':
                return 'WinLink';
            case 'Y':
                return 'C4FM Yaesu repeaters';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Red Diamond (with overlay ' . $symbolTable . ')';
                } else {
                    return null;
                }
            }

        case 'b':
            switch ($symbolTable) {
            case "\\":
                return 'Dust blowing';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Dust blowing';
                } else {
                    return null;
                }
            }

        case 'c':
            switch ($symbolTable) {
            case '\\':
                return 'Civil Defense';
            case 'D':
                return 'Decontamination';
            case 'R':
                return 'RACES';
            case 'S':
                return 'SATERN mobile canteen';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Civil Defense (with overlay ' . $symbolTable . ')';
                } else {
                    return null;
                }
            }

        case 'd':
            switch ($symbolTable) {
            case "\\":
                return 'DX Spot';
            default:
                if ($includeUndefinedOverlay) {
                    return 'DX Spot';
                } else {
                    return null;
                }
            }

        case 'e':
            switch ($symbolTable) {
            case "\\":
                return 'Sleet';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Sleet';
                } else {
                    return null;
                }
            }

        case 'f':
            switch ($symbolTable) {
            case "\\":
                return 'Funnel Cloud';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Funnel Cloud';
                } else {
                    return null;
                }
            }

        case 'g':
            switch ($symbolTable) {
            case "\\":
                return 'Gale warning flags';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Gale warning flags (with overlay ' . $symbolTable . ')';
                } else {
                    return null;
                }
            }

        case 'h':
            switch ($symbolTable) {
            case '\\':
                return 'Store/Ham Store';
            case 'F':
                return 'Hamfest';
            case 'H':
                return 'Home Dept etc..';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Other store (with overlay ' . $symbolTable . ')';
                } else {
                    return null;
                }
            }
        case 'i':
            switch ($symbolTable) {
            case "\\":
                return 'Point of interest';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Point of interest (with overlay ' . $symbolTable . ')';
                } else {
                    return null;
                }
            }

        case 'j':
            switch ($symbolTable) {
            case "\\":
                return 'WorkZone';
            default:
                if ($includeUndefinedOverlay) {
                    return 'WorkZone';
                } else {
                    return null;
                }
            }

        case 'k':
            switch ($symbolTable) {
            case '\\':
                return 'Special Vehicle (SUV)';
            case '4':
                return 'Special Vehicle (4x4)';
            case 'A':
                return 'Special Vehicle (ATV)';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Special Vehicle (with overlay ' . $symbolTable . ')';
                } else {
                    return null;
                }
            }

        case 'l':
            switch ($symbolTable) {
            case "\\":
                return 'No Symbol';
            default:
                if ($includeUndefinedOverlay) {
                    return 'No Symbol';
                } else {
                    return null;
                }
            }

        case 'm':
            switch ($symbolTable) {
            case "\\":
                return 'Milepost';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Milepost';
                } else {
                    return null;
                }
            }

        case 'n':
            switch ($symbolTable) {
            case "\\":
                return 'Red Triangle';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Red Triangle (with overlay ' . $symbolTable . ')';
                } else {
                    return null;
                }
            }

        case 'o':
            switch ($symbolTable) {
            case "\\":
                return 'Small Circle';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Small Circle (with overlay ' . $symbolTable . ')';
                } else {
                    return null;
                }
            }

        case 'p':
            switch ($symbolTable) {
            case "\\":
                return 'Partly Cloudy';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Partly Cloudy';
                } else {
                    return null;
                }
            }

        case 'q':
            switch ($symbolTable) {
            case "\\":
                return 'No Symbol';
            default:
                if ($includeUndefinedOverlay) {
                    return 'No Symbol';
                } else {
                    return null;
                }
            }

        case 'r':
            switch ($symbolTable) {
            case "\\":
                return 'Restrooms';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Restrooms';
                } else {
                    return null;
                }
            }

        case 's':
            switch ($symbolTable) {
            case '\\':
                return 'Ship/Boat';
            case '6':
                return 'Ship/Boat (Shipwreck "deep6")';
            case 'B':
                return 'Ship/Boat (Pleasure Boat)';
            case 'C':
                return 'Ship/Boat (Cargo)';
            case 'D':
                return 'Ship/Boat (Diving)';
            case 'E':
                return 'Ship/Boat (Emergency or Medical transport)';
            case 'F':
                return 'Ship/Boat (Fishing)';
            case 'H':
                return 'Ship/Boat (High-speed Craft)';
            case 'J':
                return 'Ship/Boat (Jet Ski)';
            case 'L':
                return 'Ship/Boat (Law enforcement)';
            case 'M':
                return 'Ship/Boat (Miltary)';
            case 'O':
                return 'Ship/Boat (Oil Rig)';
            case 'P':
                return 'Ship/Boat (Pilot Boat)';
            case 'Q':
                return 'Ship/Boat (Torpedo)';
            case 'S':
                return 'Ship/Boat (Search and Rescue)';
            case 'T':
                return 'Ship/Boat (Tug)';
            case 'U':
                return 'Ship/Boat (Underwater ops or submarine)';
            case 'W':
                return 'Ship/Boat (Wing-in-Ground effect or Hovercraft)';
            case 'X':
                return 'Ship/Boat (Passenger, Ferry)';
            case 'Y':
                return 'Ship/Boat (Sailing, large ship)';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Ship/Boat (with overlay ' . $symbolTable . ')';
                } else {
                    return null;
                }
            }
        case 't':
            switch ($symbolTable) {
            case "\\":
                return 'Tornado';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Tornado';
                } else {
                    return null;
                }
            }

        case 'u':
            switch ($symbolTable) {
            case '\\':
                return 'Truck';
            case 'B':
                return 'Truck (Buldozer/construction/Backhoe)';
            case 'G':
                return 'Truck (Gas)';
            case 'P':
                return 'Truck (Plow or SnowPlow)';
            case 'T':
                return 'Truck (Tanker)';
            case 'C':
                return 'Truck (Chlorine Tanker)';
            case 'H':
                return 'Truck (Hazardous)';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Truck (with overlay ' . $symbolTable . ')';
                } else {
                    return null;
                }
            }

        case 'v':
            switch ($symbolTable) {
            case "\\":
                return 'Van';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Van (with overlay ' . $symbolTable . ')';
                } else {
                    return null;
                }
            }

        case 'w':
            switch ($symbolTable) {
            case "\\":
                return 'Flooding';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Flooding';
                } else {
                    return null;
                }
            }

        case 'x':
            switch ($symbolTable) {
            case "\\":
                return 'No Symbol';
            default:
                if ($includeUndefinedOverlay) {
                    return 'No Symbol';
                } else {
                    return null;
                }
            }

        case 'y':
            switch ($symbolTable) {
            case "\\":
                return 'Skywarn';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Skywarn';
                } else {
                    return null;
                }
            }

        case 'z':
            switch ($symbolTable) {
            case '\\':
                return 'Shelter';
            case 'C':
                return 'Clinic';
            case 'G':
                return 'Government building';
            case 'M':
                return 'Morgue';
            case 'T':
                return 'Triage';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Building (with overlay ' . $symbolTable . ')';
                } else {
                    return null;
                }
            }

        case '{':
            switch ($symbolTable) {
            case "\\":
                return 'Fog';
            default:
                if ($includeUndefinedOverlay) {
                    return 'Fog';
                } else {
                    return null;
                }
            }

        case '|':
            switch ($symbolTable) {
            case "\\":
                return 'TNC Stream Switch';
            default:
                if ($includeUndefinedOverlay) {
                    return 'TNC Stream Switch';
                } else {
                    return null;
                }
            }

        case '}':
            switch ($symbolTable) {
            case "\\":
                return 'No Symbol';
            default:
                if ($includeUndefinedOverlay) {
                    return 'No Symbol';
                } else {
                    return null;
                }
            }

        case '~':
            switch ($symbolTable) {
            case "\\":
                return 'TNC Stream Switch';
            default:
                if ($includeUndefinedOverlay) {
                    return 'TNC Stream Switch';
                } else {
                    return null;
                }
            }
        }
    }
}


/**
 * Returnes true if we may show data older than 24h
 *
 * @return boolean
 */
function isAllowedToShowOlderData() {
    $isAllowedToShowOlderData = false;
    $config = parse_ini_file(ROOT . '/../config/trackdirect.ini', true);

    if (isset($config['websocket_server'])) {
        if (isset($config['websocket_server']['allow_time_travel'])) {
            if ($config['websocket_server']['allow_time_travel'] == '1') {
                $isAllowedToShowOlderData = true;
            }
        }

        if (isset($config['websocket_server']['aprs_source_id1']) && $config['websocket_server']['aprs_source_id1'] == 5) {
            // Data source is OGN, disable time travel (server will block it anyway)
            $isAllowedToShowOlderData = false;
        }

        if (isset($config['websocket_server']['aprs_source_id2']) && $config['websocket_server']['aprs_source_id2'] == 5) {
            // Data source is OGN, disable time travel (server will block it anyway)
            $isAllowedToShowOlderData = false;
        }
    }

    return $isAllowedToShowOlderData;
}

/**
 * Returnes valid view path
 *
 * @param {string} $request
 * @return string
 */
function getView($request) {
    $parts = explode("/", trim($request, '/'));
    if (count($parts) >= 2) {
        $view = array_pop($parts);
        $dir = array_pop($parts);
        if ($view && $dir == 'views') {
            $path = ROOT . '/public/views';
            foreach (scandir($path) as $file) {
                if ($file == $view) {
                    return "$path/$view";
                }
            }
        }
    }
    return null;
}

/**
 * Returnes an assoc array containing website related values from config
 *
 * @param {string} $key
 * @return string
 * */
function getWebsiteConfig($key) {
    $config = parse_ini_file(ROOT . '/../config/trackdirect.ini', true);
    if (isset($config['website']) && isset($config['website'][$key])) {
        return $config['website'][$key];
    }

    return null;
}

/**
 * Convert coordinate to pixel position in heatmap image
 *
 * @param {float} $lat
 * @param {int} $zoom
 * @param {int} $imageTileSize
 * @return int
 */
function getLatPixelCoordinate($lat, $zoom, $imageTileSize) {
    $pixelGlobeSize = $imageTileSize * pow(2, $zoom);
    $yPixelsToRadiansRatio = $pixelGlobeSize / (2 * M_PI);
    $halfPixelGlobeSize = $pixelGlobeSize / 2;
    $pixelGlobeCenterY = $halfPixelGlobeSize;
    $degreesToRadiansRatio = 180 / M_PI;
    $siny = sin($lat * M_PI / 180);

    # Truncating to 0.9999 effectively limits latitude to 89.189. This is
    # about a third of a tile past the edge of the world tile.
    if ($siny < -0.9999) {
        $siny = -0.9999;
    }
    if ($siny > 0.9999) {
        $siny = 0.9999;
    }
    $latY = round($pixelGlobeCenterY + 0.5 * log((1 + $siny) / (1 - $siny)) * -$yPixelsToRadiansRatio);
    return $latY;
}

/**
 * Convert coordinate to pixel position in heatmap image
 *
 * @param {float} $lng
 * @param {int} $zoom
 * @param {int} $imageTileSize
 * @return int
 */
function getLngPixelCoordinate($lng, $zoom, $imageTileSize) {
    $scale = 1 << $zoom;
    $lngX = floor($imageTileSize * (0.5 + $lng / 360) * $scale);
    return $lngX;
}

/**
 * Convert pixel position in heatmap image to coordinate
 *
 * @param {float} $latPixelCoord
 * @param {int} $zoom
 * @param {int} $imageTileSize
 * @return float
 */
function getLatFromLatPixelCoordinate($latPixelCoord, $zoom, $imageTileSize) {
    $pixelGlobeSize = $imageTileSize * pow(2, $zoom);
    $yPixelsToRadiansRatio = $pixelGlobeSize / (2 * M_PI);
    $halfPixelGlobeSize = $pixelGlobeSize / 2;
    $pixelGlobeCenterY = $halfPixelGlobeSize;
    $degreesToRadiansRatio = 180 / M_PI;
    $lat = (2 * atan(exp(($latPixelCoord - $pixelGlobeCenterY) / -$yPixelsToRadiansRatio)) - M_PI / 2) * $degreesToRadiansRatio;
    return $lat;
}

/**
 * Convert pixel position in heatmap image to coordinate
 *
 * @param {float} $lngPixelCoord
 * @param {int} $zoom
 * @param {int} $imageTileSize
 * @return float
 */
function getLngFromLngPixelCoordinate($lngPixelCoord, $zoom, $imageTileSize) {
    $scale = 1 << $zoom;
    $lng = ((($lngPixelCoord / $scale) / $imageTileSize) - 0.5) * 360;
    return $lng;
}

