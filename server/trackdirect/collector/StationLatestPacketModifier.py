from trackdirect.database.PacketTableCreator import PacketTableCreator


class StationLatestPacketModifier():
    """The StationLatestPacketModifier class contains functionality to modify the station latest packet
    """

    def __init__(self, db):
        """The __init__ method.

        Args:
            db (psycopg2.Connection): Database connection
        """
        self.db = db
        self.packetTableCreator = PacketTableCreator(db)

    def updateStationLatestConfirmedPacket(self, packetIdList, timestamp):
        """Updates several stations latest confirmed packet based on the specified list of packet id's

        Args:
            packetIdList (array):  Array of packet id's that should be used to set the latest confirmed packets on related stations
            timestamp (int):       Unix timestamp which is in the same date as the receive date of all packets (UTC)

        Returns:
            number of updated stations
        """
        if (packetIdList):
            packetTable = self.packetTableCreator.getPacketTable(timestamp)
            cur = self.db.cursor()
            sql = cur.mogrify("""
                update station set latest_sender_id = packet.sender_id,
                    latest_confirmed_packet_id = packet.id,
                    latest_confirmed_marker_id = packet.marker_id,
                    latest_confirmed_packet_timestamp = packet.timestamp,
                    latest_confirmed_symbol = packet.symbol,
                    latest_confirmed_symbol_table = packet.symbol_table,
                    latest_confirmed_latitude = packet.latitude,
                    latest_confirmed_longitude = packet.longitude,
                    latest_location_packet_id = packet.id,
                    latest_location_packet_timestamp = packet.timestamp,
                    latest_packet_id = packet.id,
                    latest_packet_timestamp = packet.timestamp
                from """ + packetTable + """ packet
                where packet.station_id = station.id
                    and packet.id in %s""", (tuple(packetIdList),))
            cur.execute(sql)
            rowCount = cur.rowcount

            cur.close()
            return rowCount
        return 0

    def updateStationLatestLocationPacket(self, packetIdList, timestamp):
        """Updates several stations latest location packet based on the specified list of packet id's

        Args:
            packetIdList (array):  Array of packet id's that should be used to set the latest location packets on related stations
            timestamp (int):       Unix timestamp which is in the same date as the receive date of all packets (UTC)

        Returns:
            number of updated stations
        """
        if (packetIdList):
            packetTable = self.packetTableCreator.getPacketTable(timestamp)
            cur = self.db.cursor()
            sql = cur.mogrify("""
                update station set latest_location_packet_id = packet.id,
                    latest_location_packet_timestamp = packet.timestamp,
                    latest_packet_id = packet.id,
                    latest_packet_timestamp = packet.timestamp
                from """ + packetTable + """ packet
                where packet.station_id = station.id
                    and packet.id in %s""", (tuple(packetIdList),))
            cur.execute(sql)
            rowCount = cur.rowcount

            cur.close()
            return rowCount
        return 0

    def updateStationLatestPacket(self, packetIdList, timestamp):
        """Updates several stations latest packet based on the specified list of packet id's

        Args:
            packetIdList (array):  Array of packet id's that should be used to set the latest packets on related stations
            timestamp (int):       Unix timestamp which is in the same date as the receive date of all packets (UTC)

        Returns:
            number of updated stations
        """
        if (packetIdList):
            packetTable = self.packetTableCreator.getPacketTable(timestamp)
            cur = self.db.cursor()
            sql = cur.mogrify("""
                update station set latest_packet_id = packet.id,
                    latest_packet_timestamp = packet.timestamp
                from """ + packetTable + """ packet
                where packet.station_id = station.id
                    and packet.id in %s""", (tuple(packetIdList),))
            cur.execute(sql)
            rowCount = cur.rowcount

            cur.close()
            return rowCount
        return 0


    def updateStationLatestTelemetryPacket(self, packetIdList, timestamp):
        """Updates several stations latest telemetry packet based on the specified list of packet id's

        Args:
            packetIdList (array):  Array of packet id's that should be used to set the latest packets on related stations
            timestamp (int):       Unix timestamp which is in the same date as the receive date of all packets (UTC)

        Returns:
            number of updated stations
        """
        if (packetIdList):
            packetTable = self.packetTableCreator.getPacketTable(timestamp)
            cur = self.db.cursor()
            sql = cur.mogrify("""
                update station set latest_telemetry_packet_id = packet.id,
                    latest_telemetry_packet_timestamp = packet.timestamp
                from """ + packetTable + """ packet
                where packet.station_id = station.id
                    and packet.id in %s""", (tuple(packetIdList),))
            cur.execute(sql)
            rowCount = cur.rowcount

            cur.close()
            return rowCount
        return 0

    def updateStationLatestOgnPacket(self, packetIdList, timestamp):
        """Updates several stations latest OGN packet based on the specified list of packet id's

        Args:
            packetIdList (array):  Array of packet id's that should be used to set the latest packets on related stations
            timestamp (int):       Unix timestamp which is in the same date as the receive date of all packets (UTC)

        Returns:
            number of updated stations
        """
        if (packetIdList):
            packetTable = self.packetTableCreator.getPacketTable(timestamp)
            cur = self.db.cursor()
            sql = cur.mogrify("""
                update station set latest_ogn_packet_id = packet_ogn.packet_id,
                    latest_ogn_packet_timestamp = packet_ogn.timestamp,
                    latest_ogn_sender_address = packet_ogn.ogn_sender_address,
                    latest_ogn_aircraft_type_id = packet_ogn.ogn_aircraft_type_id,
                    latest_ogn_address_type_id = packet_ogn.ogn_address_type_id
                from """ + packetTable + """_ogn packet_ogn
                where packet_ogn.station_id = station.id
                    and packet_ogn.packet_id in %s""", (tuple(packetIdList),))
            cur.execute(sql)
            rowCount = cur.rowcount
            cur.close()
            return rowCount
        return 0

    def updateStationLatestWeatherPacket(self, packetIdList, timestamp):
        """Updates several stations latest weather packet based on the specified list of packet id's

        Args:
            packetIdList (array):  Array of packet id's that should be used to set the latest packets on related stations
            timestamp (int):       Unix timestamp which is in the same date as the receive date of all packets (UTC)

        Returns:
            number of updated stations
        """
        if (packetIdList):
            packetTable = self.packetTableCreator.getPacketTable(timestamp)
            cur = self.db.cursor()
            sql = cur.mogrify("""
                update station set latest_weather_packet_id = packet.id,
                    latest_weather_packet_timestamp = packet.timestamp,
                    latest_weather_packet_comment = packet.comment
                from """ + packetTable + """ packet
                where packet.station_id = station.id
                    and packet.id in %s""", (tuple(packetIdList),))
            cur.execute(sql)
            rowCount = cur.rowcount

            cur.close()
            return rowCount
        return 0