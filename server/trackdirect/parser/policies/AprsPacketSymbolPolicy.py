class AprsPacketSymbolPolicy():
    """The AprsPacketSymbolPolicy class can answer APRS symbol related questions for a specified packet symbol characters.
    """

    def __init__(self):
        """The __init__ method.
        """
        self.primarySymbolMoving = []
        self.primarySymbolStationary = []
        self.primarySymbolMaybeMoving = []

        self.alternativeSymbolMoving = []
        self.alternativeSymbolStationary = []
        self.alternativeSymbolMaybeMoving = []

        self.primarySymbolWeather = []
        self.alternativeSymbolWeather = []

        self._initSymbolArrays()

    def isMovingSymbol(self, symbol, symbolTable):
        """Returns true is symbol indicates that station is of moving type

        Args:
            symbol (string):        The symbol character
            symbolTable (string):   The symbol table character

        Returns:
            Boolean
        """
        if (symbolTable == "/"):
            # Primary symbol
            if (symbol in self.primarySymbolMoving):
                return True
        else:
            # Alternative Symbol
            if (symbol in self.alternativeSymbolMoving):
                return True
        return False

    def isMaybeMovingSymbol(self, symbol, symbolTable):
        """Returns true is symbol indicates that station maybe is moving

        Note:
            "maybe moving" means that station should be treated as it's stationary, but you should allways be ready to change your mind and treat it as moving.

        Args:
            symbol (string):        The symbol character
            symbolTable (string):   The symbol table character

        Returns:
            Boolean
        """
        if (symbolTable == "/"):
            # Primary symbol
            if (symbol in self.primarySymbolMaybeMoving):
                return True
        else:
            # Alternative Symbol
            if (symbol in self.alternativeSymbolMaybeMoving):
                return True
        return False

    def isStationarySymbol(self, symbol, symbolTable):
        """Returns true is symbol indicates that station seems to be stationary

        Args:
            symbol (string):        The symbol character
            symbolTable (string):   The symbol table character

        Returns:
            Boolean
        """
        if (symbolTable == "/"):
            # Primary symbol
            if (symbol in self.primarySymbolStationary):
                return True
        else:
            # Alternative Symbol
            if (symbol in self.alternativeSymbolStationary):
                return True
        return False

    def isWeatherSymbol(self, symbol, symbolTable):
        """Returns true is symbol seems to be a weather station symbol

        Args:
            symbol (string):        The symbol character
            symbolTable (string):   The symbol table character

        Returns:
            Boolean
        """
        if (symbolTable == "/"):
            # Primary symbol
            if (symbol in self.primarySymbolWeather):
                return True
        else:
            # Alternative Symbol
            if (symbol in self.alternativeSymbolWeather):
                return True
        return False

    def _initSymbolArrays(self):
        """Init the symbol arrays
        """
        # If we are not sure if it is moving or not we should set it to maybe moving
        # A station marked as stationary will not get a tail on map (it will get a new marker Id for each new position), until a certain limit
        self.primarySymbolStationary.append('!')  # BB  Police, Sheriff
        self.primarySymbolStationary.append('"')  # BC  reserved  (was rain)
        self.primarySymbolStationary.append('#')  # BD  DIGI (white center)
        self.primarySymbolMaybeMoving.append('$')  # BE  PHONE
        self.primarySymbolStationary.append('%')  # BF  DX CLUSTER
        self.primarySymbolStationary.append('&')  # BG  HF GATEway
        self.primarySymbolMaybeMoving.append(
            '\'')  # BH  Small AIRCRAFT (SSID-11)
        self.primarySymbolMoving.append('(')  # BI  Mobile Satellite Station
        self.primarySymbolMaybeMoving.append(
            ')')  # BJ  Wheelchair (handicapped)
        self.primarySymbolMoving.append('*')  # BK  SnowMobile
        self.primarySymbolStationary.append('+')  # BL  Red Cross
        self.primarySymbolStationary.append(',')  # BM  Boy Scouts
        self.primarySymbolStationary.append('-')  # BN  House QTH (VHF)
        self.primarySymbolStationary.append('.')  # BO  X
        self.primarySymbolMaybeMoving.append('/')  # BP  Red Dot
        self.primarySymbolMaybeMoving.append('0')  # P0  # circle (obsolete)
        self.primarySymbolMaybeMoving.append(
            '1')  # P1  TBD (these were numbered)
        self.primarySymbolMaybeMoving.append(
            '2')  # P2  TBD (circles like pool)
        self.primarySymbolMaybeMoving.append('3')  # P3  TBD (balls.  But with)
        self.primarySymbolMaybeMoving.append('4')  # P4  TBD (overlays, we can)
        self.primarySymbolMaybeMoving.append(
            '5')  # P5  TBD (put all #'s on one)
        self.primarySymbolMaybeMoving.append(
            '6')  # P6  TBD (So 1-9 are available)
        self.primarySymbolMaybeMoving.append('7')  # P7  TBD (for new uses?)
        self.primarySymbolMaybeMoving.append(
            '8')  # P8  TBD (They are often used)
        self.primarySymbolMaybeMoving.append(
            '9')  # P9  TBD (as mobiles at events)
        self.primarySymbolStationary.append(':')  # MR  FIRE
        self.primarySymbolMaybeMoving.append(
            ';')  # MS  Campground (Portable ops)
        self.primarySymbolMoving.append('<')  # MT  Motorcycle     (SSID-10)
        self.primarySymbolMaybeMoving.append('=')  # MU  RAILROAD ENGINE
        self.primarySymbolMoving.append('>')  # MV  CAR            (SSID-9)
        self.primarySymbolStationary.append('?')  # MW  SERVER for Files
        self.primarySymbolStationary.append('@')  # MX  HC FUTURE predict (dot)
        self.primarySymbolStationary.append('A')  # PA  Aid Station
        self.primarySymbolStationary.append('B')  # PB  BBS or PBBS
        self.primarySymbolMoving.append('C')  # PC  Canoe
        self.primarySymbolStationary.append('D')  # PD
        self.primarySymbolStationary.append('E')  # PE  EYEBALL (Events, etc!)
        self.primarySymbolMoving.append('F')  # PF  Farm Vehicle (tractor)
        self.primarySymbolStationary.append('G')  # PG  Grid Square (6 digit)
        self.primarySymbolStationary.append('H')  # PH  HOTEL (blue bed symbol)
        self.primarySymbolStationary.append(
            'I')  # PI  TcpIp on air network stn
        self.primarySymbolStationary.append('J')  # PJ
        self.primarySymbolStationary.append('K')  # PK  School
        self.primarySymbolMaybeMoving.append('L')  # PL  PC user (Jan 03)
        self.primarySymbolMaybeMoving.append('M')  # PM  MacAPRS
        self.primarySymbolStationary.append('N')  # PN  NTS Station
        self.primarySymbolMoving.append('O')  # PO  BALLOON        (SSID-11)
        self.primarySymbolMaybeMoving.append('P')  # PP  Police
        self.primarySymbolStationary.append('Q')  # PQ  TBD
        self.primarySymbolMaybeMoving.append(
            'R')  # PR  REC. VEHICLE   (SSID-13)
        self.primarySymbolMaybeMoving.append('S')  # PS  SHUTTLE
        self.primarySymbolStationary.append('T')  # PT  SSTV
        self.primarySymbolMoving.append('U')  # PU  BUS            (SSID-2)
        self.primarySymbolStationary.append('V')  # PV  ATV
        self.primarySymbolStationary.append(
            'W')  # PW  National WX Service Site
        self.primarySymbolMaybeMoving.append(
            'X')  # PX  HELO           (SSID-6)
        self.primarySymbolMoving.append('Y')  # PY  YACHT (sail)   (SSID-5)
        self.primarySymbolMaybeMoving.append('Z')  # PZ  WinAPRS
        self.primarySymbolMoving.append('[')  # HS  Human/Person   (SSID-7)
        self.primarySymbolStationary.append('\\')  # HT  TRIANGLE(DF station)
        self.primarySymbolStationary.append(
            ']')  # HU  MAIL/PostOffice(was PBBS)
        self.primarySymbolMaybeMoving.append('^')  # HV  LARGE AIRCRAFT
        self.primarySymbolStationary.append('_')  # HW  WEATHER Station (blue)
        self.primarySymbolStationary.append('`')  # HX  Dish Antenna
        self.primarySymbolMaybeMoving.append('a')  # LA  AMBULANCE     (SSID-1)
        self.primarySymbolMoving.append('b')  # LB  BIKE          (SSID-4)
        self.primarySymbolStationary.append('c')  # LC  Incident Command Post
        self.primarySymbolStationary.append('d')  # LD  Fire dept
        self.primarySymbolMoving.append('e')  # LE  HORSE (equestrian)
        self.primarySymbolMaybeMoving.append('f')  # LF  FIRE TRUCK    (SSID-3)
        self.primarySymbolMoving.append('g')  # LG  Glider
        self.primarySymbolStationary.append('h')  # LH  HOSPITAL
        self.primarySymbolStationary.append(
            'i')  # LI  IOTA (islands on the air)
        self.primarySymbolMoving.append('j')  # LJ  JEEP          (SSID-12)
        self.primarySymbolMoving.append('k')  # LK  TRUCK         (SSID-14)
        self.primarySymbolMaybeMoving.append(
            'l')  # LL  Laptop (Jan 03)  (Feb 07)
        self.primarySymbolStationary.append('m')  # LM  Mic-E Repeater
        self.primarySymbolStationary.append('n')  # LN  Node (black bulls-eye)
        self.primarySymbolStationary.append('o')  # LO  EOC
        self.primarySymbolMoving.append('p')  # LP  ROVER (puppy, or dog)
        self.primarySymbolStationary.append(
            'q')  # LQ  GRID SQ shown above 128 m
        self.primarySymbolStationary.append(
            'r')  # LR  Repeater         (Feb 07)
        self.primarySymbolMoving.append('s')  # LS  SHIP (pwr boat)  (SSID-8)
        self.primarySymbolStationary.append('t')  # LT  TRUCK STOP
        self.primarySymbolMoving.append('u')  # LU  TRUCK (18 wheeler)
        self.primarySymbolMoving.append('v')  # LV  VAN           (SSID-15)
        self.primarySymbolStationary.append('w')  # LW  WATER station
        self.primarySymbolStationary.append('x')  # LX  xAPRS (Unix)
        self.primarySymbolStationary.append('y')  # LY  YAGI @ QTH
        self.primarySymbolStationary.append('z')  # LZ  TBD
        self.primarySymbolStationary.append('{')  # J1
        self.primarySymbolStationary.append('|')  # J2  TNC Stream Switch
        self.primarySymbolStationary.append('}')  # J3
        self.primarySymbolStationary.append('~')  # J4  TNC Stream Switch

        self.alternativeSymbolStationary.append(
            '!')  # OBO EMERGENCY (and overlays)
        self.alternativeSymbolStationary.append('"')  # OC  reserved
        self.alternativeSymbolStationary.append(
            '#')  # OD# OVERLAY DIGI (green star)
        self.alternativeSymbolStationary.append(
            '$')  # OEO Bank or ATM  (green box)
        self.alternativeSymbolStationary.append(
            '%')  # OFO Power Plant with overlay
        self.alternativeSymbolStationary.append(
            '&')  # OG# I=Igte R=RX T=1hopTX 2=2hopTX
        self.alternativeSymbolStationary.append(
            '\'')  # OHO Crash (& now Incident sites)
        self.alternativeSymbolStationary.append(
            '(')  # OIO CLOUDY (other clouds w ovrly)
        # OJO Firenet MEO, MODIS Earth Obs.
        self.alternativeSymbolStationary.append(')')
        self.alternativeSymbolStationary.append(
            '*')  # OK  AVAIL (SNOW moved to ` ovly S)
        self.alternativeSymbolStationary.append('+')  # OL  Church
        self.alternativeSymbolStationary.append(',')  # OM  Girl Scouts
        self.alternativeSymbolStationary.append(
            '-')  # ONO House (H=HF) (O = Op Present)
        self.alternativeSymbolStationary.append(
            '.')  # OO  Ambiguous (Big Question mark)
        self.alternativeSymbolStationary.append(
            '/')  # OP  Waypoint Destination
        self.alternativeSymbolStationary.append(
            '0')  # A0# CIRCLE (IRLP/Echolink/WIRES)
        self.alternativeSymbolStationary.append('1')  # A1  AVAIL
        self.alternativeSymbolStationary.append('2')  # A2  AVAIL
        self.alternativeSymbolStationary.append('3')  # A3  AVAIL
        self.alternativeSymbolStationary.append('4')  # A4  AVAIL
        self.alternativeSymbolStationary.append('5')  # A5  AVAIL
        self.alternativeSymbolStationary.append('6')  # A6  AVAIL
        self.alternativeSymbolStationary.append('7')  # A7  AVAIL
        self.alternativeSymbolMaybeMoving.append(
            '8')  # A8O 802.11 or other network node
        self.alternativeSymbolStationary.append(
            '9')  # A9  Gas Station (blue pump)
        self.alternativeSymbolStationary.append(
            ':')  # NR  AVAIL (Hail ==> ` ovly H)
        self.alternativeSymbolStationary.append(
            ';')  # NSO Park/Picnic + overlay events
        self.alternativeSymbolStationary.append(
            '<')  # NTO ADVISORY (one WX flag)
        self.alternativeSymbolMaybeMoving.append(
            '=')  # NUO APRStt Touchtone (DTMF users)
        self.alternativeSymbolMoving.append(
            '>')  # NV# OVERLAYED CARs & Vehicles
        self.alternativeSymbolStationary.append(
            '?')  # NW  INFO Kiosk  (Blue box with ?)
        self.alternativeSymbolStationary.append('@')  # NX  HURICANE/Trop-Storm
        self.alternativeSymbolStationary.append(
            'A')  # AA# overlayBOX DTMF & RFID & XO
        self.alternativeSymbolStationary.append(
            'B')  # AB  AVAIL (BlwngSnow ==> E ovly B
        self.alternativeSymbolStationary.append('C')  # AC  Coast Guard
        self.alternativeSymbolStationary.append(
            'D')  # ADO  DEPOTS (Drizzle ==> ' ovly D)
        self.alternativeSymbolStationary.append(
            'E')  # AE  Smoke (& other vis codes)
        self.alternativeSymbolStationary.append(
            'F')  # AF  AVAIL (FrzngRain ==> `F)
        self.alternativeSymbolStationary.append(
            'G')  # AG  AVAIL (Snow Shwr ==> I ovly S)
        self.alternativeSymbolStationary.append(
            'H')  # AHO \Haze (& Overlay Hazards)
        self.alternativeSymbolStationary.append('I')  # AI  Rain Shower
        # AJ  AVAIL (Lightening ==> I ovly L)
        self.alternativeSymbolStationary.append('J')
        self.alternativeSymbolMaybeMoving.append('K')  # AK  Kenwood HT (W)
        self.alternativeSymbolStationary.append('L')  # AL  Lighthouse
        self.alternativeSymbolStationary.append(
            'M')  # AMO MARS (A=Army,N=Navy,F=AF)
        self.alternativeSymbolStationary.append('N')  # AN  Navigation Buoy
        self.alternativeSymbolMaybeMoving.append(
            'O')  # AO  Overlay Balloon (Rocket = \O)
        # AP  Parking  [Some cars use this when they stop]
        self.alternativeSymbolMaybeMoving.append('P')
        self.alternativeSymbolStationary.append('Q')  # AQ  QUAKE
        self.alternativeSymbolStationary.append('R')  # ARO Restaurant
        self.alternativeSymbolMoving.append('S')  # AS  Satellite/Pacsat
        self.alternativeSymbolStationary.append('T')  # AT  Thunderstorm
        self.alternativeSymbolStationary.append('U')  # AU  SUNNY
        self.alternativeSymbolStationary.append('V')  # AV  VORTAC Nav Aid
        self.alternativeSymbolStationary.append(
            'W')  # AW# # NWS site (NWS options)
        self.alternativeSymbolStationary.append(
            'X')  # AX  Pharmacy Rx (Apothicary)
        self.alternativeSymbolMaybeMoving.append('Y')  # AYO Radios and devices
        self.alternativeSymbolStationary.append('Z')  # AZ  AVAIL
        self.alternativeSymbolMaybeMoving.append(
            '[')  # DSO W.Cloud (& humans w Ovrly)
        self.alternativeSymbolMaybeMoving.append(
            '\\')  # DTO New overlayable GPS symbol
        self.alternativeSymbolStationary.append(']')  # DU  AVAIL
        self.alternativeSymbolMaybeMoving.append(
            '^')  # DV# other Aircraft ovrlys (2014)
        self.alternativeSymbolStationary.append(
            '_')  # DW# # WX site (green digi)
        self.alternativeSymbolStationary.append(
            '`')  # DX  Rain (all types w ovrly)
        self.alternativeSymbolStationary.append(
            'a')  # SA#O ARRL,ARES,WinLINK,Dstar, etc
        self.alternativeSymbolStationary.append(
            'b')  # SB  AVAIL(Blwng Dst/Snd => E ovly)
        self.alternativeSymbolStationary.append(
            'c')  # SC#O CD triangle RACES/SATERN/etc
        self.alternativeSymbolStationary.append('d')  # SD  DX spot by callsign
        self.alternativeSymbolStationary.append(
            'e')  # SE  Sleet (& future ovrly codes)
        self.alternativeSymbolStationary.append('f')  # SF  Funnel Cloud
        self.alternativeSymbolStationary.append('g')  # SG  Gale Flags
        self.alternativeSymbolStationary.append(
            'h')  # SHO Store. or HAMFST Hh=HAM store
        self.alternativeSymbolStationary.append(
            'i')  # SI# BOX or points of Interest
        self.alternativeSymbolMaybeMoving.append(
            'j')  # SJ  WorkZone (Steam Shovel)
        # SKO Special Vehicle SUV,ATV,4x4
        self.alternativeSymbolMoving.append('k')
        self.alternativeSymbolStationary.append(
            'l')  # SL  Areas(box,circles,etc)
        self.alternativeSymbolStationary.append(
            'm')  # SM  Value Sign (3 digit display)
        self.alternativeSymbolStationary.append('n')  # SN# OVERLAY TRIANGLE
        self.alternativeSymbolStationary.append('o')  # SO  small circle
        self.alternativeSymbolStationary.append(
            'p')  # SP  AVAIL (PrtlyCldy => ( ovly P
        self.alternativeSymbolStationary.append('q')  # SQ  AVAIL
        self.alternativeSymbolStationary.append('r')  # SR  Restrooms
        self.alternativeSymbolMoving.append('s')  # SS# OVERLAY SHIP/boats
        self.alternativeSymbolStationary.append('t')  # ST  Tornado
        self.alternativeSymbolMoving.append('u')  # SU# OVERLAYED TRUCK
        self.alternativeSymbolMoving.append('v')  # SV# OVERLAYED Van
        self.alternativeSymbolStationary.append(
            'w')  # SWO Flooding (Avalanches/Slides)
        self.alternativeSymbolStationary.append(
            'x')  # SX  Wreck or Obstruction ->X<-
        self.alternativeSymbolStationary.append('y')  # SY  Skywarn
        self.alternativeSymbolStationary.append('z')  # SZ# OVERLAYED Shelter
        self.alternativeSymbolStationary.append(
            '{')  # Q1  AVAIL? (Fog ==> E ovly F)
        self.alternativeSymbolStationary.append('|')  # Q2  TNC Stream Switch
        self.alternativeSymbolStationary.append('}')  # Q3  AVAIL? (maybe)
        self.alternativeSymbolStationary.append('~')  # Q4  TNC Stream Switch

        self.primarySymbolWeather.append('W')  # PW  National WX Service Site
        self.primarySymbolWeather.append('_')  # HW  WEATHER Station (blue)

        self.alternativeSymbolWeather.append(
            '(')  # OIO CLOUDY (other clouds w ovrly)
        # OK  AVAIL (SNOW moved to ` ovly S)
        self.alternativeSymbolWeather.append('*')
        self.alternativeSymbolWeather.append(
            ':')  # NR  AVAIL (Hail ==> ` ovly H)
        self.alternativeSymbolWeather.append('@')  # NX  HURICANE/Trop-Storm
        self.alternativeSymbolWeather.append(
            'B')  # AB  AVAIL (BlwngSnow ==> E ovly B
        # ADO  DEPOTS (Drizzle ==> ' ovly D)
        self.alternativeSymbolWeather.append('D')
        self.alternativeSymbolWeather.append(
            'F')  # AF  AVAIL (FrzngRain ==> `F)
        # AG  AVAIL (Snow Shwr ==> I ovly S)
        self.alternativeSymbolWeather.append('G')
        self.alternativeSymbolWeather.append(
            'H')  # AHO \Haze (& Overlay Hazards)
        self.alternativeSymbolWeather.append('I')  # AI  Rain Shower
        # AJ  AVAIL (Lightening ==> I ovly L)
        self.alternativeSymbolWeather.append('J')
        self.alternativeSymbolWeather.append('T')  # AT  Thunderstorm
        self.alternativeSymbolWeather.append('U')  # AU  SUNNY
        self.alternativeSymbolWeather.append(
            '[')  # DSO W.Cloud (& humans w Ovrly)
        self.alternativeSymbolWeather.append('_')  # DW# # WX site (green digi)
        self.alternativeSymbolWeather.append(
            '`')  # DX  Rain (all types w ovrly)
        # SB  AVAIL(Blwng Dst/Snd => E ovly)
        self.alternativeSymbolWeather.append('b')
        # SE  Sleet (& future ovrly codes)
        self.alternativeSymbolWeather.append('e')
        self.alternativeSymbolWeather.append('f')  # SF  Funnel Cloud
        # SP  AVAIL (PrtlyCldy => ( ovly P
        self.alternativeSymbolWeather.append('p')
        self.alternativeSymbolWeather.append('t')  # ST  Tornado
        self.alternativeSymbolWeather.append('y')  # SY  Skywarn
        self.alternativeSymbolWeather.append(
            '{')  # Q1  AVAIL? (Fog ==> E ovly F)
