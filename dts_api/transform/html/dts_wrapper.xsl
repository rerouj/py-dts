<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:dts="https://w3id.org/dts/api#" xmlns:tei="http://www.tei-c.org/ns/1.0"
    version="1.0">
    <xsl:output method="html" encoding="UTF-8" media-type="text/html" indent="yes"/>
    <xsl:strip-space elements="tei:*"/>
    <xsl:template match="/">
        <html>
            <head>
                <title>
                    <xsl:value-of select="//tei:title"/>
                </title>
            </head>
            <body>
                <h1><xsl:value-of select="//tei:title"/></h1>
                <p>
                    <xsl:for-each select="//dts:wrapper/descendant-or-self::*/text()">
                        <xsl:value-of select="normalize-space(.)"/>
                    </xsl:for-each>
                </p>
            </body>
        </html>
    </xsl:template>
</xsl:stylesheet>