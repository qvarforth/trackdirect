import time
from math import ceil

from server.trackdirect.TrackDirectConfig import TrackDirectConfig
from server.trackdirect.parser.policies.MapSectorPolicy import MapSectorPolicy

class WebsocketConnectionState:
    """An instance contains information about the current state of a websocket connection."""

    def __init__(self):
        """Initialize the WebsocketConnectionState."""
        self.filter_station_id_dict = {}
        self.latest_sw_lng = 0
        self.latest_sw_lat = 0
        self.latest_ne_lng = 0
        self.latest_ne_lat = 0
        self.only_latest_packet_requested = None
        self.latest_time_travel_request = None
        self.latest_minutes_request = 60
        self.max_map_sector_overwrite_packet_timestamp_dict = {}
        self.max_map_sector_packet_timestamp_dict = {}
        self.max_all_station_timestamp_dict = {}
        self.max_complete_station_timestamp_dict = {}
        self.stations_on_map_dict = {}
        self.latest_request_type = None
        self.latest_request_timestamp = 0
        self.latest_requestId = 0
        self.latest_handled_request_id = 0
        self.config = TrackDirectConfig()
        self.no_real_time = False
        self.disconnected = False

    def is_reset(self):
        """Returns True if state just has been reset."""
        return not (self.stations_on_map_dict or
                    self.max_complete_station_timestamp_dict or
                    self.max_all_station_timestamp_dict or
                    self.max_map_sector_packet_timestamp_dict or
                    self.max_map_sector_overwrite_packet_timestamp_dict)

    def reset(self):
        """Reset information related to what stations have been added to the map."""
        self.stations_on_map_dict = {}
        self.max_complete_station_timestamp_dict = {}
        self.max_all_station_timestamp_dict = {}
        self.max_map_sector_packet_timestamp_dict = {}
        self.max_map_sector_overwrite_packet_timestamp_dict = {}

    def total_reset(self):
        """Reset everything."""
        self.reset()
        self.latest_minutes_request = 60
        self.latest_time_travel_request = None
        self.only_latest_packet_requested = None
        self.latest_ne_lat = 0
        self.latest_ne_lng = 0
        self.latest_sw_lat = 0
        self.latest_sw_lng = 0
        self.filter_station_id_dict = {}

    def is_map_empty(self):
        """Returns True if map is empty."""
        return not (self.max_map_sector_packet_timestamp_dict or
                    self.max_map_sector_overwrite_packet_timestamp_dict or
                    self.max_complete_station_timestamp_dict or
                    self.max_all_station_timestamp_dict)

    def is_stations_on_map(self, station_ids):
        """Returns True if all specified stations already exist on the map."""
        return all(stationId in self.stations_on_map_dict for stationId in station_ids)

    def is_station_history_on_map(self, station_id):
        """Returns True if specified station already has its history on the map."""
        return station_id in self.max_complete_station_timestamp_dict

    def get_station_latest_timestamp_on_map(self, station_id, only_include_complete=True):
        """Returns the timestamp of the latest sent packet to client."""
        if not only_include_complete and station_id in self.max_all_station_timestamp_dict:
            return self.max_all_station_timestamp_dict[station_id]
        return self.max_complete_station_timestamp_dict.get(station_id)

    def is_valid_latest_position(self):
        """Returns True if latest requested map bounds are valid."""
        return not (self.latest_ne_lat == 0 and self.latest_ne_lng == 0 and
                    self.latest_sw_lat == 0 and self.latest_sw_lng == 0)

    def is_map_sector_known(self, map_sector):
        """Returns True if we have added any stations with complete history to this map sector."""
        return map_sector in self.max_map_sector_packet_timestamp_dict

    def get_map_sector_timestamp(self, map_sector):
        """Returns the latest handled timestamp in specified map sector."""
        if map_sector in self.max_map_sector_packet_timestamp_dict:
            return self.max_map_sector_packet_timestamp_dict[map_sector]
        if self.only_latest_packet_requested and map_sector in self.max_map_sector_overwrite_packet_timestamp_dict:
            return self.max_map_sector_overwrite_packet_timestamp_dict[map_sector]
        if self.latest_time_travel_request is not None:
            return int(self.latest_time_travel_request) - (int(self.latest_minutes_request) * 60)
        return int(time.time()) - (int(self.latest_minutes_request) * 60)

    def get_visible_map_sectors(self):
        """Get the map sectors currently visible."""
        max_lat = self.latest_ne_lat
        max_lng = self.latest_ne_lng
        min_lat = self.latest_sw_lat
        min_lng = self.latest_sw_lng

        result = []
        if max_lng < min_lng:
            result.extend(self.get_map_sectors_by_interval(min_lat, max_lat, min_lng, 180.0))
            min_lng = -180.0

        result.extend(self.get_map_sectors_by_interval(min_lat, max_lat, min_lng, max_lng))
        return result[::-1]

    def get_map_sectors_by_interval(self, min_lat, max_lat, min_lng, max_lng):
        """Get the map sectors for specified interval."""
        result = []
        map_sector_policy = MapSectorPolicy()
        min_area_code = map_sector_policy.get_map_sector(min_lat, min_lng)
        max_area_code = map_sector_policy.get_map_sector(max_lat, max_lng)
        if min_area_code is not None and max_area_code is not None:
            lng_diff = int(ceil(max_lng)) - int(ceil(min_lng))
            area_code = min_area_code
            while area_code <= max_area_code:
                if area_code % 10 == 5:
                    result.append(area_code)
                else:
                    result.append(area_code)
                    result.append(area_code + 5)

                for i in range(1, lng_diff + 1):
                    if area_code % 10 == 5:
                        result.append(area_code + (10 * i) - 5)
                        result.append(area_code + (10 * i))
                    else:
                        result.append(area_code + (10 * i))
                        result.append(area_code + (10 * i) + 5)

                area_code += 20000

        return result

    def set_latest_minutes(self, minutes, reference_time):
        """Set the latest requested number of minutes, returns True if something has changed."""
        if minutes is None:
            minutes = 60
        elif len(self.filter_station_id_dict) == 0 and int(minutes) > int(self.config.max_default_time):
            minutes = int(self.config.max_default_time)
        elif len(self.filter_station_id_dict) > 0 and int(minutes) > int(self.config.max_filter_time):
            minutes = int(self.config.max_filter_time)

        if not self.config.allow_time_travel and int(minutes) > 1440:
            minutes = 1440

        if reference_time is not None and reference_time < 0:
            reference_time = 0

        changed = False
        if self.config.allow_time_travel:
            if ((self.latest_time_travel_request is not None and reference_time is not None and
                 self.latest_time_travel_request != reference_time) or
                (self.latest_time_travel_request is not None and reference_time is None) or
                (self.latest_time_travel_request is None and reference_time is not None)):
                self.latest_time_travel_request = reference_time
                self.reset()
                changed = True

        if self.latest_minutes_request is None or self.latest_minutes_request != minutes:
            self.latest_minutes_request = minutes
            self.reset()
            changed = True
        return changed

    def set_only_latest_packet_requested(self, only_latest_packet_requested):
        """Set if only latest packets are requested or not."""
        self.only_latest_packet_requested = only_latest_packet_requested

    def set_latest_map_bounds(self, ne_lat, ne_lng, sw_lat, sw_lng):
        """Set map bounds requested by client."""
        if ne_lat is None or ne_lng is None or sw_lat is None or sw_lng is None:
            self.latest_ne_lat = 0
            self.latest_ne_lng = 0
            self.latest_sw_lat = 0
            self.latest_sw_lng = 0
        else:
            self.latest_ne_lat = ne_lat
            self.latest_ne_lng = ne_lng
            self.latest_sw_lat = sw_lat
            self.latest_sw_lng = sw_lng

    def set_map_sector_latest_overwrite_time_stamp(self, map_sector, timestamp):
        """Set a new latest handled timestamp for a map sector (overwritable type of packets)."""
        if (map_sector not in self.max_map_sector_overwrite_packet_timestamp_dict or
                self.max_map_sector_overwrite_packet_timestamp_dict[map_sector] < timestamp):
            self.max_map_sector_overwrite_packet_timestamp_dict[map_sector] = timestamp

    def set_map_sector_latest_time_stamp(self, map_sector, timestamp):
        """Set a new latest handled timestamp for a map sector."""
        if (map_sector not in self.max_map_sector_packet_timestamp_dict or
                self.max_map_sector_packet_timestamp_dict[map_sector] < timestamp):
            self.max_map_sector_packet_timestamp_dict[map_sector] = timestamp - 1

    def set_complete_station_latest_timestamp(self, station_id, timestamp):
        """Set a new latest handled timestamp for a complete station."""
        if (station_id not in self.max_complete_station_timestamp_dict or
                self.max_complete_station_timestamp_dict[station_id] < timestamp):
            self.max_complete_station_timestamp_dict[station_id] = timestamp

    def set_station_latest_timestamp(self, station_id, timestamp):
        """Set a new latest handled timestamp for a station."""
        if (station_id not in self.max_all_station_timestamp_dict or
                self.max_all_station_timestamp_dict[station_id] < timestamp):
            self.max_all_station_timestamp_dict[station_id] = timestamp

    def disable_real_time(self):
        """Disable real-time functionality."""
        self.no_real_time = True