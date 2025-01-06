class AprsPacketSymbolPolicy:
    """The AprsPacketSymbolPolicy class can answer APRS symbol related questions for a specified packet symbol characters.
    """

    def __init__(self):
        """The __init__ method.
        """
        self.primary_symbol_moving = []
        self.primary_symbol_stationary = []
        self.primary_symbol_maybe_moving = []

        self.alternative_symbol_moving = []
        self.alternative_symbol_stationary = []
        self.alternative_symbol_maybe_moving = []

        self.primary_symbol_weather = []
        self.alternative_symbol_weather = []

        self._init_symbol_arrays()

    def is_moving_symbol(self, symbol, symbol_table):
        """Returns true is symbol indicates that station is of moving type

        Args:
            symbol (string):        The symbol character
            symbol_table (string):   The symbol table character

        Returns:
            Boolean
        """
        if symbol_table == "/":
            # Primary symbol
            if symbol in self.primary_symbol_moving:
                return True
        else:
            # Alternative Symbol
            if symbol in self.alternative_symbol_moving:
                return True
        return False

    def is_maybe_moving_symbol(self, symbol, symbol_table):
        """Returns true is symbol indicates that station maybe is moving

        Note:
            "maybe moving" means that station should be treated as it's stationary, but you should allways be ready to change your mind and treat it as moving.

        Args:
            symbol (string):        The symbol character
            symbol_table (string):   The symbol table character

        Returns:
            Boolean
        """
        if symbol_table == "/":
            # Primary symbol
            if symbol in self.primary_symbol_maybe_moving:
                return True
        else:
            # Alternative Symbol
            if symbol in self.alternative_symbol_maybe_moving:
                return True
        return False

    def is_stationary_symbol(self, symbol, symbol_table):
        """Returns true is symbol indicates that station seems to be stationary

        Args:
            symbol (string):        The symbol character
            symbol_table (string):   The symbol table character

        Returns:
            Boolean
        """
        if symbol_table == "/":
            # Primary symbol
            if symbol in self.primary_symbol_stationary:
                return True
        else:
            # Alternative Symbol
            if symbol in self.alternative_symbol_stationary:
                return True
        return False

    def is_weather_symbol(self, symbol, symbol_table):
        """Returns true is symbol seems to be a weather station symbol

        Args:
            symbol (string):        The symbol character
            symbol_table (string):   The symbol table character

        Returns:
            Boolean
        """
        if symbol_table == "/":
            # Primary symbol
            if symbol in self.primary_symbol_weather:
                return True
        else:
            # Alternative Symbol
            if symbol in self.alternative_symbol_weather:
                return True
        return False

    def _init_symbol_arrays(self):
        """Init the symbol arrays
        """
        # If we are not sure if it is moving or not we should set it to maybe moving
        # A station marked as stationary will not get a tail on map (it will get a new marker Id for each new position), until a certain limit
        self.primary_symbol_stationary.append('!')  # BB  Police, Sheriff
        self.primary_symbol_stationary.append('"')  # BC  reserved  (was rain)
        self.primary_symbol_stationary.append('#')  # BD  DIGI (white center)
        self.primary_symbol_maybe_moving.append('$')  # BE  PHONE
        self.primary_symbol_stationary.append('%')  # BF  DX CLUSTER
        self.primary_symbol_stationary.append('&')  # BG  HF GATEway
        self.primary_symbol_maybe_moving.append('\'')  # BH  Small AIRCRAFT (SSID-11)
        self.primary_symbol_moving.append('(')  # BI  Mobile Satellite Station
        self.primary_symbol_maybe_moving.append(')')  # BJ  Wheelchair (handicapped)
        self.primary_symbol_moving.append('*')  # BK  SnowMobile
        self.primary_symbol_stationary.append('+')  # BL  Red Cross
        self.primary_symbol_stationary.append(',')  # BM  Boy Scouts
        self.primary_symbol_stationary.append('-')  # BN  House QTH (VHF)
        self.primary_symbol_stationary.append('.')  # BO  X
        self.primary_symbol_maybe_moving.append('/')  # BP  Red Dot
        self.primary_symbol_maybe_moving.append('0')  # P0  # circle (obsolete)
        self.primary_symbol_maybe_moving.append('1')  # P1  TBD (these were numbered)
        self.primary_symbol_maybe_moving.append('2')  # P2  TBD (circles like pool)
        self.primary_symbol_maybe_moving.append('3')  # P3  TBD (balls.  But with)
        self.primary_symbol_maybe_moving.append('4')  # P4  TBD (overlays, we can)
        self.primary_symbol_maybe_moving.append('5')  # P5  TBD (put all #'s on one)
        self.primary_symbol_maybe_moving.append('6')  # P6  TBD (So 1-9 are available)
        self.primary_symbol_maybe_moving.append('7')  # P7  TBD (for new uses?)
        self.primary_symbol_maybe_moving.append('8')  # P8  TBD (They are often used)
        self.primary_symbol_maybe_moving.append('9')  # P9  TBD (as mobiles at events)
        self.primary_symbol_stationary.append(':')  # MR  FIRE
        self.primary_symbol_maybe_moving.append(';')  # MS  Campground (Portable ops)
        self.primary_symbol_moving.append('<')  # MT  Motorcycle     (SSID-10)
        self.primary_symbol_maybe_moving.append('=')  # MU  RAILROAD ENGINE
        self.primary_symbol_moving.append('>')  # MV  CAR            (SSID-9)
        self.primary_symbol_stationary.append('?')  # MW  SERVER for Files
        self.primary_symbol_stationary.append('@')  # MX  HC FUTURE predict (dot)
        self.primary_symbol_stationary.append('A')  # PA  Aid Station
        self.primary_symbol_stationary.append('B')  # PB  BBS or PBBS
        self.primary_symbol_moving.append('C')  # PC  Canoe
        self.primary_symbol_stationary.append('D')  # PD
        self.primary_symbol_stationary.append('E')  # PE  EYEBALL (Events, etc!)
        self.primary_symbol_moving.append('F')  # PF  Farm Vehicle (tractor)
        self.primary_symbol_stationary.append('G')  # PG  Grid Square (6 digit)
        self.primary_symbol_stationary.append('H')  # PH  HOTEL (blue bed symbol)
        self.primary_symbol_stationary.append('I')  # PI  TcpIp on air network stn
        self.primary_symbol_stationary.append('J')  # PJ
        self.primary_symbol_stationary.append('K')  # PK  School
        self.primary_symbol_maybe_moving.append('L')  # PL  PC user (Jan 03)
        self.primary_symbol_maybe_moving.append('M')  # PM  MacAPRS
        self.primary_symbol_stationary.append('N')  # PN  NTS Station
        self.primary_symbol_moving.append('O')  # PO  BALLOON        (SSID-11)
        self.primary_symbol_maybe_moving.append('P')  # PP  Police
        self.primary_symbol_stationary.append('Q')  # PQ  TBD
        self.primary_symbol_maybe_moving.append('R')  # PR  REC. VEHICLE   (SSID-13)
        self.primary_symbol_maybe_moving.append('S')  # PS  SHUTTLE
        self.primary_symbol_stationary.append('T')  # PT  SSTV
        self.primary_symbol_moving.append('U')  # PU  BUS            (SSID-2)
        self.primary_symbol_stationary.append('V')  # PV  ATV
        self.primary_symbol_stationary.append('W')  # PW  National WX Service Site
        self.primary_symbol_maybe_moving.append('X')  # PX  HELO           (SSID-6)
        self.primary_symbol_moving.append('Y')  # PY  YACHT (sail)   (SSID-5)
        self.primary_symbol_maybe_moving.append('Z')  # PZ  WinAPRS
        self.primary_symbol_moving.append('[')  # HS  Human/Person   (SSID-7)
        self.primary_symbol_stationary.append('\\')  # HT  TRIANGLE(DF station)
        self.primary_symbol_stationary.append(']')  # HU  MAIL/PostOffice(was PBBS)
        self.primary_symbol_maybe_moving.append('^')  # HV  LARGE AIRCRAFT
        self.primary_symbol_stationary.append('_')  # HW  WEATHER Station (blue)
        self.primary_symbol_stationary.append('`')  # HX  Dish Antenna
        self.primary_symbol_maybe_moving.append('a')  # LA  AMBULANCE     (SSID-1)
        self.primary_symbol_moving.append('b')  # LB  BIKE          (SSID-4)
        self.primary_symbol_stationary.append('c')  # LC  Incident Command Post
        self.primary_symbol_stationary.append('d')  # LD  Fire dept
        self.primary_symbol_moving.append('e')  # LE  HORSE (equestrian)
        self.primary_symbol_maybe_moving.append('f')  # LF  FIRE TRUCK    (SSID-3)
        self.primary_symbol_moving.append('g')  # LG  Glider
        self.primary_symbol_stationary.append('h')  # LH  HOSPITAL
        self.primary_symbol_stationary.append('i')  # LI  IOTA (islands on the air)
        self.primary_symbol_moving.append('j')  # LJ  JEEP          (SSID-12)
        self.primary_symbol_moving.append('k')  # LK  TRUCK         (SSID-14)
        self.primary_symbol_maybe_moving.append('l')  # LL  Laptop (Jan 03)  (Feb 07)
        self.primary_symbol_stationary.append('m')  # LM  Mic-E Repeater
        self.primary_symbol_stationary.append('n')  # LN  Node (black bulls-eye)
        self.primary_symbol_stationary.append('o')  # LO  EOC
        self.primary_symbol_moving.append('p')  # LP  ROVER (puppy, or dog)
        self.primary_symbol_stationary.append('q')  # LQ  GRID SQ shown above 128 m
        self.primary_symbol_stationary.append('r')  # LR  Repeater         (Feb 07)
        self.primary_symbol_moving.append('s')  # LS  SHIP (pwr boat)  (SSID-8)
        self.primary_symbol_stationary.append('t')  # LT  TRUCK STOP
        self.primary_symbol_moving.append('u')  # LU  TRUCK (18 wheeler)
        self.primary_symbol_moving.append('v')  # LV  VAN           (SSID-15)
        self.primary_symbol_stationary.append('w')  # LW  WATER station
        self.primary_symbol_stationary.append('x')  # LX  xAPRS (Unix)
        self.primary_symbol_stationary.append('y')  # LY  YAGI @ QTH
        self.primary_symbol_stationary.append('z')  # LZ  TBD
        self.primary_symbol_stationary.append('{')  # J1
        self.primary_symbol_stationary.append('|')  # J2  TNC Stream Switch
        self.primary_symbol_stationary.append('}')  # J3
        self.primary_symbol_stationary.append('~')  # J4  TNC Stream Switch

        self.alternative_symbol_stationary.append('!')  # OBO EMERGENCY (and overlays)
        self.alternative_symbol_stationary.append('"')  # OC  reserved
        self.alternative_symbol_stationary.append('#')  # OD# OVERLAY DIGI (green star)
        self.alternative_symbol_stationary.append('$')  # OEO Bank or ATM  (green box)
        self.alternative_symbol_stationary.append('%')  # OFO Power Plant with overlay
        self.alternative_symbol_stationary.append('&')  # OG# I=Igte R=RX T=1hopTX 2=2hopTX
        self.alternative_symbol_stationary.append('\'')  # OHO Crash (& now Incident sites)
        self.alternative_symbol_stationary.append('(')  # OIO CLOUDY (other clouds w ovrly)
        # OJO Firenet MEO, MODIS Earth Obs.
        self.alternative_symbol_stationary.append(')')
        self.alternative_symbol_stationary.append('*')  # OK  AVAIL (SNOW moved to ` ovly S)
        self.alternative_symbol_stationary.append('+')  # OL  Church
        self.alternative_symbol_stationary.append(',')  # OM  Girl Scouts
        self.alternative_symbol_stationary.append('-')  # ONO House (H=HF) (O = Op Present)
        self.alternative_symbol_stationary.append('.')  # OO  Ambiguous (Big Question mark)
        self.alternative_symbol_stationary.append('/')  # OP  Waypoint Destination
        self.alternative_symbol_stationary.append('0')  # A0# CIRCLE (IRLP/Echolink/WIRES)
        self.alternative_symbol_stationary.append('1')  # A1  AVAIL
        self.alternative_symbol_stationary.append('2')  # A2  AVAIL
        self.alternative_symbol_stationary.append('3')  # A3  AVAIL
        self.alternative_symbol_stationary.append('4')  # A4  AVAIL
        self.alternative_symbol_stationary.append('5')  # A5  AVAIL
        self.alternative_symbol_stationary.append('6')  # A6  AVAIL
        self.alternative_symbol_stationary.append('7')  # A7  AVAIL
        self.alternative_symbol_maybe_moving.append('8')  # A8O 802.11 or other network node
        self.alternative_symbol_stationary.append('9')  # A9  Gas Station (blue pump)
        self.alternative_symbol_stationary.append(':')  # NR  AVAIL (Hail ==> ` ovly H)
        self.alternative_symbol_stationary.append(';')  # NSO Park/Picnic + overlay events
        self.alternative_symbol_stationary.append('<')  # NTO ADVISORY (one WX flag)
        self.alternative_symbol_maybe_moving.append('=')  # NUO APRStt Touchtone (DTMF users)
        self.alternative_symbol_moving.append('>')  # NV# OVERLAYED CARs & Vehicles
        self.alternative_symbol_stationary.append('?')  # NW  INFO Kiosk  (Blue box with ?)
        self.alternative_symbol_stationary.append('@')  # NX  HURICANE/Trop-Storm
        self.alternative_symbol_stationary.append('A')  # AA# overlayBOX DTMF & RFID & XO
        self.alternative_symbol_stationary.append('B')  # AB  AVAIL (BlwngSnow ==> E ovly B
        self.alternative_symbol_stationary.append('C')  # AC  Coast Guard
        self.alternative_symbol_stationary.append('D')  # ADO  DEPOTS (Drizzle ==> ' ovly D)
        self.alternative_symbol_stationary.append('E')  # AE  Smoke (& other vis codes)
        self.alternative_symbol_stationary.append('F')  # AF  AVAIL (FrzngRain ==> `F)
        self.alternative_symbol_stationary.append('G')  # AG  AVAIL (Snow Shwr ==> I ovly S)
        self.alternative_symbol_stationary.append('H')  # AHO \Haze (& Overlay Hazards)
        self.alternative_symbol_stationary.append('I')  # AI  Rain Shower
        # AJ  AVAIL (Lightening ==> I ovly L)
        self.alternative_symbol_stationary.append('J')
        self.alternative_symbol_maybe_moving.append('K')  # AK  Kenwood HT (W)
        self.alternative_symbol_stationary.append('L')  # AL  Lighthouse
        self.alternative_symbol_stationary.append('M')  # AMO MARS (A=Army,N=Navy,F=AF)
        self.alternative_symbol_stationary.append('N')  # AN  Navigation Buoy
        self.alternative_symbol_maybe_moving.append('O')  # AO  Overlay Balloon (Rocket = \O)
        # AP  Parking  [Some cars use this when they stop]
        self.alternative_symbol_maybe_moving.append('P')
        self.alternative_symbol_stationary.append('Q')  # AQ  QUAKE
        self.alternative_symbol_stationary.append('R')  # ARO Restaurant
        self.alternative_symbol_moving.append('S')  # AS  Satellite/Pacsat
        self.alternative_symbol_stationary.append('T')  # AT  Thunderstorm
        self.alternative_symbol_stationary.append('U')  # AU  SUNNY
        self.alternative_symbol_stationary.append('V')  # AV  VORTAC Nav Aid
        self.alternative_symbol_stationary.append('W')  # AW# # NWS site (NWS options)
        self.alternative_symbol_stationary.append( 'X')  # AX  Pharmacy Rx (Apothicary)
        self.alternative_symbol_maybe_moving.append('Y')  # AYO Radios and devices
        self.alternative_symbol_stationary.append('Z')  # AZ  AVAIL
        self.alternative_symbol_maybe_moving.append('[')  # DSO W.Cloud (& humans w Ovrly)
        self.alternative_symbol_maybe_moving.append('\\')  # DTO New overlayable GPS symbol
        self.alternative_symbol_stationary.append(']')  # DU  AVAIL
        self.alternative_symbol_maybe_moving.append('^')  # DV# other Aircraft ovrlys (2014)
        self.alternative_symbol_stationary.append('_')  # DW# # WX site (green digi)
        self.alternative_symbol_stationary.append('`')  # DX  Rain (all types w ovrly)
        self.alternative_symbol_stationary.append('a')  # SA#O ARRL,ARES,WinLINK,Dstar, etc
        self.alternative_symbol_stationary.append('b')  # SB  AVAIL(Blwng Dst/Snd => E ovly)
        self.alternative_symbol_stationary.append('c')  # SC#O CD triangle RACES/SATERN/etc
        self.alternative_symbol_stationary.append('d')  # SD  DX spot by callsign
        self.alternative_symbol_stationary.append('e')  # SE  Sleet (& future ovrly codes)
        self.alternative_symbol_stationary.append('f')  # SF  Funnel Cloud
        self.alternative_symbol_stationary.append('g')  # SG  Gale Flags
        self.alternative_symbol_stationary.append('h')  # SHO Store. or HAMFST Hh=HAM store
        self.alternative_symbol_stationary.append('i')  # SI# BOX or points of Interest
        self.alternative_symbol_maybe_moving.append('j')  # SJ  WorkZone (Steam Shovel)
        # SKO Special Vehicle SUV,ATV,4x4
        self.alternative_symbol_moving.append('k')
        self.alternative_symbol_stationary.append('l')  # SL  Areas(box,circles,etc)
        self.alternative_symbol_stationary.append('m')  # SM  Value Sign (3 digit display)
        self.alternative_symbol_stationary.append('n')  # SN# OVERLAY TRIANGLE
        self.alternative_symbol_stationary.append('o')  # SO  small circle
        self.alternative_symbol_stationary.append('p')  # SP  AVAIL (PrtlyCldy => ( ovly P
        self.alternative_symbol_stationary.append('q')  # SQ  AVAIL
        self.alternative_symbol_stationary.append('r')  # SR  Restrooms
        self.alternative_symbol_moving.append('s')  # SS# OVERLAY SHIP/boats
        self.alternative_symbol_stationary.append('t')  # ST  Tornado
        self.alternative_symbol_moving.append('u')  # SU# OVERLAYED TRUCK
        self.alternative_symbol_moving.append('v')  # SV# OVERLAYED Van
        self.alternative_symbol_stationary.append('w')  # SWO Flooding (Avalanches/Slides)
        self.alternative_symbol_stationary.append('x')  # SX  Wreck or Obstruction ->X<-
        self.alternative_symbol_stationary.append('y')  # SY  Skywarn
        self.alternative_symbol_stationary.append('z')  # SZ# OVERLAYED Shelter
        self.alternative_symbol_stationary.append('{')  # Q1  AVAIL? (Fog ==> E ovly F)
        self.alternative_symbol_stationary.append('|')  # Q2  TNC Stream Switch
        self.alternative_symbol_stationary.append('}')  # Q3  AVAIL? (maybe)
        self.alternative_symbol_stationary.append('~')  # Q4  TNC Stream Switch

        self.primary_symbol_weather.append('W')  # PW  National WX Service Site
        self.primary_symbol_weather.append('_')  # HW  WEATHER Station (blue)

        self.alternative_symbol_weather.append('(')  # OIO CLOUDY (other clouds w ovrly)
        # OK  AVAIL (SNOW moved to ` ovly S)
        self.alternative_symbol_weather.append('*')
        self.alternative_symbol_weather.append(':')  # NR  AVAIL (Hail ==> ` ovly H)
        self.alternative_symbol_weather.append('@')  # NX  HURICANE/Trop-Storm
        self.alternative_symbol_weather.append('B')  # AB  AVAIL (BlwngSnow ==> E ovly B
        # ADO  DEPOTS (Drizzle ==> ' ovly D)
        self.alternative_symbol_weather.append('D')
        self.alternative_symbol_weather.append('F')  # AF  AVAIL (FrzngRain ==> `F)
        # AG  AVAIL (Snow Shwr ==> I ovly S)
        self.alternative_symbol_weather.append('G')
        self.alternative_symbol_weather.append('H')  # AHO \Haze (& Overlay Hazards)
        self.alternative_symbol_weather.append('I')  # AI  Rain Shower
        # AJ  AVAIL (Lightening ==> I ovly L)
        self.alternative_symbol_weather.append('J')
        self.alternative_symbol_weather.append('T')  # AT  Thunderstorm
        self.alternative_symbol_weather.append('U')  # AU  SUNNY
        self.alternative_symbol_weather.append('[')  # DSO W.Cloud (& humans w Ovrly)
        self.alternative_symbol_weather.append('_')  # DW# # WX site (green digi)
        self.alternative_symbol_weather.append('`')  # DX  Rain (all types w ovrly)
        # SB  AVAIL(Blwng Dst/Snd => E ovly)
        self.alternative_symbol_weather.append('b')
        # SE  Sleet (& future ovrly codes)
        self.alternative_symbol_weather.append('e')
        self.alternative_symbol_weather.append('f')  # SF  Funnel Cloud
        # SP  AVAIL (PrtlyCldy => ( ovly P
        self.alternative_symbol_weather.append('p')
        self.alternative_symbol_weather.append('t')  # ST  Tornado
        self.alternative_symbol_weather.append('y')  # SY  Skywarn
        self.alternative_symbol_weather.append('{')  # Q1  AVAIL? (Fog ==> E ovly F)