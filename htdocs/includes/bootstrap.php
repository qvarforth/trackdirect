<?php
define('ROOT', dirname(dirname(__FILE__)));

require_once ROOT . '/includes/autoload.php';
require_once ROOT . '/includes/common.php';

date_default_timezone_set("UTC");

ini_set("error_reporting", "true");
error_reporting(E_ALL|E_STRCT);

ini_set("display_errors", "false");