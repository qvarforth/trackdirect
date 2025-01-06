import logging

from server.trackdirect.common.Repository import Repository
from server.trackdirect.objects.Station import Station
from server.trackdirect.database.DatabaseObjectFinder import DatabaseObjectFinder
from server.trackdirect.database.PacketTableCreator import PacketTableCreator
from server.trackdirect.exceptions.TrackDirectMissingStationError import TrackDirectMissingStationError


class StationRepository(Repository):
    """A Repository class for the Station class."""

    # Static class variables
    station_id_cache = {}
    station_name_cache = {}

    def __init__(self, db):
        """Initialize the StationRepository with a database connection."""
        super().__init__(db)
        self.logger = logging.getLogger('trackdirect')
        self.db_object_finder = DatabaseObjectFinder(db)
        self.packet_table_creator = PacketTableCreator(db)

    def get_object_by_id(self, id):
        """Return a Station object based on the specified id in the database."""
        with self.db.cursor() as cursor:
            cursor.execute("SELECT * FROM station WHERE id = %s", (id,))
            record = cursor.fetchone()
            return self.get_object_from_record(record) if record else self.create()

    def get_object_list_by_station_id_list(self, station_id_list):
        """Return a list of Station objects based on a list of station ids."""
        with self.db.cursor() as cursor:
            cursor.execute("SELECT * FROM station WHERE id IN %s", (tuple(station_id_list),))
            return [self.get_object_from_record(record) for record in cursor if record]

    def get_tiny_object_list(self):
        """Return a list of all station ids and their latest packet timestamps."""
        with self.db.cursor() as cursor:
            cursor.execute("SELECT id, latest_packet_timestamp FROM station ORDER BY id")
            return [self.create_from_id_and_timestamp(record) for record in cursor if record]

    def get_object_list(self):
        """Return a list of all Station objects."""
        with self.db.cursor() as cursor:
            cursor.execute("SELECT * FROM station ORDER BY id")
            return [self.get_object_from_record(record) for record in cursor]

    def get_object_list_by_name(self, name, station_type_id=None, source_id=None, min_timestamp=0):
        """Return a list of stations based on the specified name."""
        if source_id == 3:
            source_id = 1

        query = "SELECT * FROM station WHERE name = %s AND latest_confirmed_packet_timestamp > %s"
        params = [name, min_timestamp]

        if station_type_id is not None:
            query += " AND station_type_id = %s"
            params.append(station_type_id)

        if source_id is not None:
            query += " AND (source_id = %s OR source_id IS NULL)"
            params.append(source_id)

        with self.db.cursor() as cursor:
            cursor.execute(query, tuple(params))
            return [self.get_object_from_record(record) for record in cursor]

    def get_object_by_name(self, name, source_id, station_type_id=1, create_new_if_missing=True):
        """Return a Station object based on the specified name."""
        if source_id == 3:
            source_id = 1

        query = "SELECT * FROM station WHERE name = %s"
        params = [name.strip()]

        if source_id is not None:
            query += " AND (source_id IS NULL OR source_id = %s)"
            params.append(source_id)

        query += " ORDER BY id DESC"

        with self.db.cursor() as cursor:
            cursor.execute(query, tuple(params))
            record = cursor.fetchone()

        db_object = self.get_object_from_record(record) if record else self.create()

        if record:
            if db_object.source_id is None or db_object.source_id != source_id:
                db_object.source_id = source_id
                db_object.save()
            if db_object.station_type_id != station_type_id and station_type_id == 1:
                db_object.station_type_id = station_type_id
                db_object.save()
        elif create_new_if_missing:
            db_object.name = name
            db_object.source_id = source_id
            db_object.station_type_id = station_type_id
            db_object.save()

        return db_object

    def get_object_list_by_search_parameter(self, search_parameter, min_timestamp, limit):
        """Return an array of the latest packet objects specified by search_parameter."""
        search_parameter = search_parameter.strip().replace('%', r"\%").replace('*', '%')
        result = []

        with self.db.cursor() as cursor:
            if self.db_object_finder.check_table_exists('ogn_device'):
                cursor.execute("SELECT * FROM ogn_device LIMIT 1")
                if cursor.fetchone():
                    cursor.execute(
                        """SELECT * FROM station WHERE latest_confirmed_packet_timestamp IS NOT NULL 
                        AND latest_confirmed_packet_timestamp > %s 
                        AND latest_ogn_sender_address IS NOT NULL 
                        AND EXISTS (SELECT 1 FROM ogn_device WHERE registration ILIKE %s AND device_id = station.latest_ogn_sender_address) 
                        LIMIT %s""",
                        (min_timestamp, search_parameter, limit - len(result))
                    )
                    result.extend(self.get_object_from_record(record) for record in cursor)

                if len(result) < limit:
                    cursor.execute(
                        """SELECT * FROM station WHERE latest_confirmed_packet_timestamp IS NOT NULL 
                        AND latest_confirmed_packet_timestamp > %s 
                        AND latest_ogn_sender_address ILIKE %s 
                        LIMIT %s""",
                        (min_timestamp, search_parameter, limit - len(result))
                    )
                    result.extend(self.get_object_from_record(record) for record in cursor)

            if len(result) < limit:
                cursor.execute(
                    """SELECT * FROM station WHERE latest_confirmed_packet_timestamp IS NOT NULL 
                    AND latest_confirmed_packet_timestamp > %s 
                    AND name ILIKE %s 
                    LIMIT %s""",
                    (min_timestamp, search_parameter, limit - len(result))
                )
                result.extend(self.get_object_from_record(record) for record in cursor)

        return result

    def get_cached_object_by_id(self, station_id):
        """Get Station based on station id."""
        if station_id not in StationRepository.station_id_cache:
            station = self.get_object_by_id(station_id)
            if station.is_existing_object():
                self._update_cache(StationRepository.station_id_cache, station_id, station)
                return station
        else:
            return StationRepository.station_id_cache.get(station_id)

        raise TrackDirectMissingStationError('No station with specified id found')

    def get_cached_object_by_name(self, station_name, source_id):
        """Get Station based on station name."""
        if source_id == 3:
            source_id = 1

        key = hash(f"{station_name};{source_id}" if source_id is not None else station_name)
        if key not in StationRepository.station_name_cache:
            station = self.get_object_by_name(station_name, source_id, None, False)
            if station.is_existing_object():
                self._update_cache(StationRepository.station_name_cache, key, station)
                return station
        else:
            return StationRepository.station_name_cache.get(key)

        raise TrackDirectMissingStationError('No station with specified station name found')

    def get_object_from_record(self, record):
        """Return a Station object based on the specified database record dict."""
        db_object = self.create()
        if record:
            db_object.id = int(record["id"])
            db_object.name = record["name"]
            db_object.latest_sender_id = int(record["latest_sender_id"]) if record["latest_sender_id"] is not None else None
            db_object.station_type_id = int(record["station_type_id"])
            db_object.source_id = int(record["source_id"]) if record["source_id"] is not None else None
            db_object.latest_location_packet_id = record["latest_location_packet_id"]
            db_object.latest_location_packet_timestamp = record["latest_location_packet_timestamp"]
            db_object.latest_confirmed_packet_id = record["latest_confirmed_packet_id"]
            db_object.latest_confirmed_packet_timestamp = record["latest_confirmed_packet_timestamp"]
            db_object.latest_confirmed_symbol = record["latest_confirmed_symbol"]
            db_object.latest_confirmed_symbol_table = record["latest_confirmed_symbol_table"]
            db_object.latest_confirmed_latitude = record["latest_confirmed_latitude"]
            db_object.latest_confirmed_longitude = record["latest_confirmed_longitude"]
            db_object.latest_confirmed_marker_id = record["latest_confirmed_marker_id"]
            db_object.latest_packet_id = record["latest_packet_id"]
            db_object.latest_packet_timestamp = record["latest_packet_timestamp"]
            db_object.latest_weather_packet_id = record["latest_weather_packet_id"]
            db_object.latest_weather_packet_timestamp = record["latest_weather_packet_timestamp"]
            db_object.latest_telemetry_packet_id = record["latest_telemetry_packet_id"]
            db_object.latest_telemetry_packet_timestamp = record["latest_telemetry_packet_timestamp"]
            db_object.latest_ogn_packet_id = record["latest_ogn_packet_id"]
            db_object.latest_ogn_packet_timestamp = record["latest_ogn_packet_timestamp"]
            db_object.latest_ogn_sender_address = record["latest_ogn_sender_address"]
            db_object.latest_ogn_aircraft_type_id = record["latest_ogn_aircraft_type_id"]
            db_object.latest_ogn_address_type_id = record["latest_ogn_address_type_id"]

        return db_object

    def create(self):
        """Create an empty Station object."""
        return Station(self.db)

    def create_from_id_and_timestamp(self, record):
        """Create a Station object from id and latest packet timestamp."""
        db_object = self.create()
        db_object.id = int(record["id"])
        db_object.latest_packet_timestamp = record["latest_packet_timestamp"]
        return db_object

    def _update_cache(self, cache, key, station):
        """Update the cache with a new station object."""
        max_number_of_stations = 100
        if len(cache) > max_number_of_stations:
            cache.clear()
        cache[key] = station