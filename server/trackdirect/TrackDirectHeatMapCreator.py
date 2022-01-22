import logging
import heatmap
import random
import psycopg2
import psycopg2.extras
from math import floor, ceil, sqrt, degrees, asinh, tan, radians, sin, asin, atan, exp
from math import log as math_log
from math import pi as math_pi
import datetime
import time
import image_slicer
from PIL import ImageDraw, ImageFont
import os
import shutil
from twisted.python import log

from trackdirect.database.DatabaseConnection import DatabaseConnection


class TrackDirectHeatMapCreator():
    """The TrackDirectHeatMapCreator class is built to generate heatmaps based on the track direct database data.

    Note:
        The heatmaps are divided into several tiles to make them smaller to download and to make the heatmap generator less memory intensive
    """

    def __init__(self, destinationDir):
        """The __init__ method.

        Args:
            destinationDir (String):   Absolute path to the destination directory
        """
        self.destinationDir = destinationDir

        dbConnection = DatabaseConnection()
        self.db = dbConnection.getConnection(True)
        self.db.set_isolation_level(0)

        # We can not create one image for large zoom, heatmap lib has a limit and RAM-usage will be huge
        self.minZoomForOneImage = 3

        # Recommended tile size is 256 (or 512 if main usage is mobile phones with retina display)
        self.imageTileSize = 256

        self.logger = logging.getLogger(__name__)

    def run(self):
        """Start creating heatmap images and deploy them when done.
        """
        self._createHeatMapImages()

        # Deploy new images
        self._renameHeatMapImagesToGoogleMapStandard()

    def _createHeatMapImages(self):
        """Start creating heatmap images
        """
        # Zoom 0: = 1
        # Zoom 1: 2x2 = 4
        # Zoom 2: 4x4 = 16
        # Zoom 3: 8x8 = 64 (This is the largest that we create as one single image)
        # Zoom 4: 16x16 = 256
        # Zoom 5: 32x32 = 1024
        # Zoom 6: 64x64
        # Zoom 7: 128x128
        for zoom in range(0, 8):
            if (zoom <= self.minZoomForOneImage):
                partsLength = 1
                parts = range(0, partsLength)
                imageSize = pow(2, zoom) * self.imageTileSize
                numberOfTilesPerImage = pow(2, zoom) * pow(2, zoom)
            else:
                partsLength = pow(2, zoom-self.minZoomForOneImage) * \
                    pow(2, zoom-self.minZoomForOneImage)
                parts = range(0, partsLength)
                numberOfTilesPerImage = pow(
                    2, self.minZoomForOneImage) * pow(2, self.minZoomForOneImage)
                imageSize = pow(2, self.minZoomForOneImage) * \
                    self.imageTileSize

            # For zoom 0-3 we only have one part
            # zoom 4: 4 parts (images)
            # zoom 5: 16 parts (images)
            # zoom 6: 64 parts (images)
            # zoom 7: 256 parts (images)
            # all images will alter be splitted into tile of size 256x256
            for part in parts:
                # We are not in any hurry so we sleep to lower the effect on other processes (we are on a shared server)
                time.sleep(1)

                totalMinLat = float(-85.05115)
                totalMaxLat = float(85.05115)
                totalMinLng = float(-180)
                totalMaxLng = float(180)

                totalMinLatPixel = float(
                    self._getLatPixelCoordinate(totalMinLat, zoom))
                totalMaxLatPixel = float(
                    self._getLatPixelCoordinate(totalMaxLat, zoom))
                totalMinLngPixel = float(
                    self._getLngPixelCoordinate(totalMinLng, zoom))
                totalMaxLngPixel = float(
                    self._getLngPixelCoordinate(totalMaxLng, zoom))

                if (zoom <= self.minZoomForOneImage):
                    minLat = totalMinLat
                    maxLat = totalMaxLat
                    minLng = totalMinLng
                    maxLng = totalMaxLng

                    minLatPixel = totalMinLatPixel
                    maxLatPixel = totalMaxLatPixel
                    minLngPixel = totalMinLngPixel
                    maxLngPixel = totalMaxLngPixel
                else:
                    latPartPixelLength = (totalMinLatPixel) / sqrt(partsLength)
                    lngPartPixelLength = (totalMaxLngPixel) / sqrt(partsLength)

                    partRow = floor(part / sqrt(partsLength))  # Starts on 0
                    partColumn = part - \
                        sqrt(partsLength) * partRow  # Starts on 0

                    minLatPixel = (partRow * latPartPixelLength) + \
                        latPartPixelLength
                    maxLatPixel = (partRow * latPartPixelLength)
                    minLngPixel = totalMinLngPixel + partColumn * lngPartPixelLength
                    maxLngPixel = totalMinLngPixel + \
                        ((partColumn * lngPartPixelLength) + lngPartPixelLength)

                    minLat = self._getLatFromLatPixelCoordinate(
                        minLatPixel, zoom)
                    maxLat = self._getLatFromLatPixelCoordinate(
                        maxLatPixel, zoom)
                    minLng = self._getLngFromLngPixelCoordinate(
                        minLngPixel, zoom)
                    maxLng = self._getLngFromLngPixelCoordinate(
                        maxLngPixel, zoom)

                file = self.destinationDir + "/latest-heatmap." + \
                    str(zoom)+"."+str(part)+".png"

                #pts = [(random.uniform(minLat, maxLat), random.uniform(minLng, maxLng)) for i in range(1000)]
                pts = self._getPoints(minLat, maxLat, minLng, maxLng, zoom)

                if (len(pts) == 0):
                    self.logger.info("Skipping file:" + file)
                else:
                    # Create the heatmap!
                    hm = heatmap.Heatmap()
                    dotSize = 2*(zoom+1)
                    opacity = 230
                    size = (imageSize, imageSize)
                    schema = "fire"

                    #area = ((0, minLatProj), (maxLngProj*2, maxLatProj))
                    area = ((minLngPixel, minLatPixel),
                            (maxLngPixel, maxLatPixel))
                    hm.heatmap(pts, dotSize, opacity, size,
                               schema, area).save(file)
                    self.logger.info("Created file:" + file)

                    # Split heatmap into tiles
                    if (numberOfTilesPerImage > 1):
                        # The tile image filename will be :
                        # latest-heatmap.zoom.part_row_column.png
                        # Example for zoom level 4:
                        # latest-heatmap.4.0_01_01.png -> will be renamed to latest-heatmap.4.0.0.png
                        # latest-heatmap.4.0_01_02.png
                        # latest-heatmap.4.0_02_01.png
                        # latest-heatmap.4.0_02_02.png
                        # latest-heatmap.4.1_01_01.png
                        # latest-heatmap.4.1_01_02.png
                        # latest-heatmap.4.1_02_01.png
                        # latest-heatmap.4.1_02_02.png
                        # latest-heatmap.4.2_01_01.png
                        # latest-heatmap.4.2_01_02.png
                        # latest-heatmap.4.2_02_01.png
                        # latest-heatmap.4.2_02_02.png
                        # latest-heatmap.4.3_01_01.png -> will be renamed to latest-heatmap.4.3.0.png
                        # latest-heatmap.4.3_01_02.png
                        # latest-heatmap.4.3_02_01.png
                        # latest-heatmap.4.3_02_02.png

                        # Use this for production
                        image_slicer.slice(file, numberOfTilesPerImage)

                        # Use following code to print something on each tile (to make sure tile is placed correct on map)
                        #tiles = image_slicer.slice(file, numberOfTilesPerImage, save= False)
                        # for tile in tiles:
                        #    overlay = ImageDraw.Draw(tile.image)
                        #    overlay.text((5, 5), str(zoom) + ':' +str(part) + ':'+ str(tile.number), (255, 255, 255), ImageFont.load_default())
                        #image_slicer.save_tiles(tiles, directory='htdocs/public/heatmaps/', prefix="latest-heatmap."+str(zoom)+"."+str(part))

    def _renameHeatMapImagesToGoogleMapStandard(self):
        """Deploy the new heatmap images (this is done by renaming the created files)
        """
        for zoom in range(0, 8):
            if (zoom <= self.minZoomForOneImage):
                partsLength = 1
                parts = range(0, partsLength)
                imageSize = pow(2, zoom) * self.imageTileSize
                numberOfTilesPerImage = pow(2, zoom) * pow(2, zoom)
            else:
                partsLength = pow(2, zoom-self.minZoomForOneImage) * \
                    pow(2, zoom-self.minZoomForOneImage)
                parts = range(0, partsLength)
                numberOfTilesPerImage = pow(
                    2, self.minZoomForOneImage) * pow(2, self.minZoomForOneImage)
                imageSize = pow(2, self.minZoomForOneImage) * \
                    self.imageTileSize

            for part in parts:
                if (numberOfTilesPerImage == 1):
                    # This is only effects the zoom 0 file
                    os.rename(self.destinationDir + "/latest-heatmap.0.0.png",
                              self.destinationDir + "/latest-heatmap.0.0.0.png")

                else:
                    # Lets rename the files to google map standard (or something like it)
                    for row in range(1, int(sqrt(numberOfTilesPerImage)) + 1):
                        for column in range(1, int(sqrt(numberOfTilesPerImage)) + 1):
                            if (row < 10):
                                oldRowStr = '0'+str(row)
                            else:
                                oldRowStr = str(row)

                            if (column < 10):
                                oldColumStr = '0'+str(column)
                            else:
                                oldColumStr = str(column)

                            # Starts on 0
                            partRow = floor(part / sqrt(partsLength))
                            partColumn = part - \
                                sqrt(partsLength) * partRow  # Starts on 0
                            newRowStr = str(
                                int((row - 1) + (partRow * sqrt(numberOfTilesPerImage))))
                            newColumStr = str(
                                int((column - 1) + (partColumn * sqrt(numberOfTilesPerImage))))  # 1-1 + 1*8

                            oldFile = self.destinationDir + "/latest-heatmap." + \
                                str(zoom)+"."+str(part)+"_" + \
                                str(oldRowStr)+"_"+str(oldColumStr)+".png"
                            newFile = self.destinationDir + "/latest-heatmap." + \
                                str(zoom)+"."+str(newRowStr) + \
                                "."+str(newColumStr)+".png"

                            if (os.path.exists(oldFile)):
                                self.logger.info(
                                    "Renaming file : " + oldFile + " -> " + newFile)
                                os.rename(oldFile, newFile)
                            else:
                                oldFile = self.destinationDir + '/transparent.png'
                                self.logger.info(
                                    "Copy file : " + oldFile + " -> " + newFile)
                                shutil.copyfile(oldFile, newFile)

    def _getPoints(self, minLat, maxLat, minLng, maxLng, zoom):
        """Get latitude, longitude point in the specified map bounds

        Args:
            maxLat (float): The max latitude
            maxLng (float): The max longitude
            minLat (float): The min latitude
            minLng (float): The min longitude

        Returns:
            Array of points (a point is a latitude, longitude tuple)
        """
        result = []
        timestampLimit = int(time.time()) - (60*60)
        selectCursor = self.db.cursor()

        selectCursor.execute("""
            select latest_confirmed_latitude latitude, latest_confirmed_longitude longitude
            from station
            where latest_confirmed_packet_timestamp > %s
                and latest_confirmed_latitude between %s and %s
                and latest_confirmed_longitude between %s and %s""", (timestampLimit, minLat, maxLat, minLng, maxLng,))

        for record in selectCursor:
            if (record != None):
                lngProjection = self._getLngPixelCoordinate(
                    record["longitude"], zoom)
                latProjection = self._getLatPixelCoordinate(
                    record["latitude"], zoom)
                result.append((lngProjection, latProjection))
        selectCursor.close()
        return result

    def _getLatPixelCoordinate(self, lat, zoom):
        """Translate a latitude to a pixel coordinate value for a specified zoom

        Args:
            lat (float): The latitude
            zoom (int):  The zoom

        Returns:
            Returns a pixel coordinate value as an int
        """
        pixelGlobeSize = self.imageTileSize * pow(2, zoom)
        yPixelsToRadiansRatio = pixelGlobeSize / (2 * math_pi)
        halfPixelGlobeSize = float(pixelGlobeSize / 2)
        pixelGlobeCenterY = halfPixelGlobeSize
        degreesToRadiansRatio = 180 / math_pi
        siny = sin(lat * math_pi / 180)

        # Truncating to 0.9999 effectively limits latitude to 89.189. This is
        # about a third of a tile past the edge of the world tile.
        if (siny < -0.9999):
            siny = -0.9999
        if (siny > 0.9999):
            siny = 0.9999
        latY = round(pixelGlobeCenterY + .5 *
                     math_log((1 + siny) / (1 - siny)) * -yPixelsToRadiansRatio)
        return latY

    def _getLngPixelCoordinate(self, lng, zoom):
        """Translate a longitude to a pixel coordinate value for a specified zoom

        Args:
            lng (float): The longitude
            zoom (int):  The zoom

        Returns:
            Returns a pixel coordinate value as an int
        """
        scale = 1 << zoom
        lngX = floor(self.imageTileSize * (0.5 + lng / 360) * scale)
        return lngX

    def _getLatFromLatPixelCoordinate(self, latPixelCoord, zoom):
        """Translate a pixel coordinate value to a latitude for a specified zoom

        Args:
            latPixelCoord (int): The pixel coordinate value
            zoom (int):          The zoom

        Returns:
            Returns a latitude as a float
        """
        pixelGlobeSize = self.imageTileSize * pow(2, zoom)
        yPixelsToRadiansRatio = pixelGlobeSize / (2 * math_pi)
        halfPixelGlobeSize = float(pixelGlobeSize / 2)
        pixelGlobeCenterY = halfPixelGlobeSize
        degreesToRadiansRatio = 180 / math_pi
        lat = (2 * atan(exp((latPixelCoord - pixelGlobeCenterY) / -
               yPixelsToRadiansRatio)) - math_pi / 2) * degreesToRadiansRatio
        return lat

    def _getLngFromLngPixelCoordinate(self, lngPixelCoord, zoom):
        """Translate a pixel coordinate value to a longitude for a specified zoom

        Args:
            lngPixelCoord (int): The pixel coordinate value
            zoom (int):          The zoom

        Returns:
            Returns a longitude as a float
        """
        scale = 1 << zoom
        lng = (((lngPixelCoord / scale) / self.imageTileSize) - 0.5) * 360
        return lng
