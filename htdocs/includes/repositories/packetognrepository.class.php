<?php

class PacketOgnRepository extends ModelRepository
{

    private static $_singletonInstance = null;

    public function __construct()
    {
        parent::__construct('PacketOgn');
    }

    /**
     * Returnes an initiated PacketOgnRepository
     *
     * @return PacketOgnRepository
     */
    public static function getInstance()
    {
        if (self::$_singletonInstance === null) {
            self::$_singletonInstance = new PacketOgnRepository();
        }

        return self::$_singletonInstance;
    }

    /**
     * Get object by id
     *
     * @param  int $id
     * @return PacketOgn
     */
    public function getObjectById($id)
    {
        if (!isInt($id)) {
            return new PacketOgn(0);
        }
        return $this->getObjectFromSql('select * from packet_ogn where id = ?', [$id]);
    }

    /**
     * Get object by packet id
     *
     * @param  int $id
     * @return PacketOgn
     */
    public function getObjectByPacketId($packetId)
    {
        if (!isInt($packetId)) {
            return new PacketOgn(0);
        }
        return $this->getObjectFromSql('select * from packet_ogn where packet_id = ?', [$packetId]);
    }
}
