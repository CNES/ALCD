<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="2.14.9-Essen" minimumScale="0" maximumScale="1e+08" hasScaleBasedVisibilityFlag="0">
  <pipe>
    <rasterrenderer opacity="1" alphaBand="0" classificationMax="6" classificationMinMaxOrigin="CumulativeCutFullExtentEstimated" band="1" classificationMin="2" type="singlebandpseudocolor">
      <rasterTransparency/>
      <rastershader>
        <colorrampshader colorRampType="INTERPOLATED" clip="0">
          <item alpha="255" value="0" label="land" color="#009738"/>
          <item alpha="255" value="1" label="water" color="#008ed0"/>
          <item alpha="255" value="2" label="clouds shadows" color="#0a0a0a"/>
          <item alpha="255" value="3" label="snow" color="#4d4d4d"/>
          <item alpha="255" value="4" label="low clouds" color="#d2d2d2"/>
          <item alpha="255" value="255" label="null value" color="#c3ff2a"/>
        </colorrampshader>
      </rastershader>
    </rasterrenderer>
    <brightnesscontrast brightness="0" contrast="0"/>
    <huesaturation colorizeGreen="128" colorizeOn="0" colorizeRed="255" colorizeBlue="128" grayscaleMode="0" saturation="0" colorizeStrength="100"/>
    <rasterresampler maxOversampling="2"/>
  </pipe>
  <blendMode>0</blendMode>
</qgis>
