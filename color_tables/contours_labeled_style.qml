<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="2.14.11-Essen" minimumScale="0" maximumScale="1e+08" hasScaleBasedVisibilityFlag="0">
  <pipe>
    <rasterrenderer opacity="1" alphaBand="-1" classificationMax="6" classificationMinMaxOrigin="CumulativeCutFullExtentEstimated" band="1" classificationMin="2" type="singlebandpseudocolor">
      <rasterTransparency/>
      <rastershader>
        <colorrampshader colorRampType="INTERPOLATED" clip="0">
          <item alpha="255" value="0" label="null value" color="#c3ff2a"/>
          <item alpha="0" value="1" label="background" color="#bb533a"/>
          <item alpha="255" value="2" label="low clouds" color="#b0ff00"/>
          <item alpha="255" value="3" label="high clouds" color="#f016ff"/>
          <item alpha="255" value="4" label="clouds shadows" color="#0a0a0a"/>
          <item alpha="0" value="5" label="land" color="#009738"/>
          <item alpha="255" value="6" label="water" color="#008ed0"/>
          <item alpha="255" value="7" label="snow" color="#4d4d4d"/>
        </colorrampshader>
      </rastershader>
    </rasterrenderer>
    <brightnesscontrast brightness="0" contrast="0"/>
    <huesaturation colorizeGreen="128" colorizeOn="0" colorizeRed="255" colorizeBlue="128" grayscaleMode="0" saturation="0" colorizeStrength="100"/>
    <rasterresampler maxOversampling="2"/>
  </pipe>
  <blendMode>0</blendMode>
</qgis>
