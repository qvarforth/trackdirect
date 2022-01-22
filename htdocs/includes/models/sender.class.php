<?php

class Sender extends Model
{
    public function __construct($id)
    {
        parent::__construct($id);
    }

    /**
     * Get sender station
     *
     * @return Station
     */
    public function getSenderStationObject()
    {
        return StationRepository::getInstance()->getObjectByNameAndSenderId($this->name, $this->id);
    }
}
