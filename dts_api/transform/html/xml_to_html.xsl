<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:tei="http://www.tei-c.org/ns/1.0"
    exclude-result-prefixes="xs" version="2.0">
    <xsl:output method="html" encoding="UTF-8" media-type="text/html" indent="yes"></xsl:output>
    <xsl:strip-space elements="tei:*"/>
    <xsl:template match="//tei:TEI/tei:text/tei:body">
        <html>
            <head>
                <title>
                    <xsl:value-of select="//tei:title"/>
                </title>
            </head>
            <body>
                <h1><xsl:value-of select="//tei:title"/></h1>
                <xsl:for-each select="//tei:p">
                    <p>
                        <xsl:for-each select="node()">
                            <xsl:choose>
                                <xsl:when test="contains(.,'-')">
                                    <xsl:value-of select="normalize-space(translate(.,'-',''))"/>
                                </xsl:when>
                                <xsl:otherwise>
                                    <xsl:value-of select="normalize-space(.)"/>
                                </xsl:otherwise>
                            </xsl:choose>
                        </xsl:for-each>
                    </p>
                </xsl:for-each>
            </body>
        </html>
    </xsl:template>
</xsl:stylesheet>