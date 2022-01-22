<?php

class Model
{

    protected $_id;
    protected $_values;

    public function __construct($id)
    {
        $this->_id = $id;
    }

    /**
     * Returns id of the object
     *
     * @return int
     */
    public function getId()
    {
        return $this->_id;
    }

    /**
     * Returns true if object exists in database
     *
     * @return boolean
     */
    public function isExistingObject()
    {
        if ($this->_id != null) {
            return true;
        }
        return false;
    }

    /**
     * Makes it possible to get $object->field
     *
     * @param string $key
     */
    public function __get($key)
    {
        $key = $this->_camelize($key);

        if (isset($this->_values[$key])) {
            return $this->_values[$key];
        } else {
            return null;
        }
    }


    /**
     * Makes it possible to set $object->field
     *
     * @param string $key
     * @param mixed
     */
    public function __set($key, $value)
    {
        $this->_values[$this->_camelize($key)] = $value;
    }


    /**
     * Makes it possible to check if $object->field is set
     *
     * @param string $key
     */
    public function __isset($key)
    {
        if (isset($this->_values[$key])) {
            return true;
        } else {
            return false;
        }
    }

    /**
     * Makes it possible to unset $object->field
     *
     * @param string $key
     */
    public function __unset($key)
    {
        if (isset($this->_values[$key])) {
            unset($this->_values[$key]);
        }
    }

    /**
     * Update object from array, usually a db record
     * column-names with underscores will be converted to camelcase
     *
     * @param array $array
     */
    public function updateObjectFromArray($array)
    {
        foreach ($array as $column => $value) {
            $this->_values[$this->_camelize($column)] = $value;
        }
    }

    /**
     * Convert underscore separated variables to camelcaps
     * (for some reason I prefer underscore in db-columns but I prefer camelCaps in code...)
     *
     * @param  string $input
     * @return string
     */
    private function _camelize($input)
    {
        return lcfirst(str_replace('_', '', ucwords($input, '_')));
    }
}
