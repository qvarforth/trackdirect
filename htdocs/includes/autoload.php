<?php

/**
 * Autoload classes when needed
 *
 * @param  string $className
 * @return null
 */
function __autoload($className)
{

    if (file_exists(ROOT . '/includes/' . strtolower($className) . '.class.php')) {
        include_once ROOT . '/includes/' . strtolower($className) . '.class.php';

    } else if (file_exists(ROOT . '/includes/models/' . strtolower($className) . '.class.php')) {
        include_once ROOT . '/includes/models/' . strtolower($className) . '.class.php';

    } else if (file_exists(ROOT . '/includes/repositories/' . strtolower($className) . '.class.php')) {
        include_once ROOT . '/includes/repositories/' . strtolower($className) . '.class.php';

    } else {
        error_log(sprintf('Could not find class %s', $className));
    }
}
