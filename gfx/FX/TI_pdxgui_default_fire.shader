# My attempt at implementing https://www.rastertek.com/dx11tut33.html but it's for gui elements
# Mostly works but the movement is a bit off, need to adjust the vertex shader

Includes = {
	"cw/pdxgui.fxh"
	"cw/pdxgui_sprite.fxh"
	"standardfuncsgfx.fxh"
}

VertexStruct VS_INDOMITA_GUI_FIRE_INPUT
{
	float2 Position					: POSITION;
	float4 LeftTop_WidthHeight		: TEXCOORD0;
	float4 UVLeftTop_WidthHeight	: TEXCOORD1;
	float4 Color					: COLOR0;
};

VertexStruct VS_INDOMITA_GUI_FIRE_OUTPUT
{
	float4 Position			: PDX_POSITION;
	float2 UV0				: TEXCOORD0;
	float2 texCoords1		: TEXCOORD1;
	float2 texCoords2		: TEXCOORD2;
	float2 texCoords3 		: TEXCOORD3;
	float4 Color			: COLOR0;
};

VertexShader =
{
	Code
	[[
		VS_INDOMITA_GUI_FIRE_OUTPUT IndomitaGuiFireVertexShader( VS_INDOMITA_GUI_FIRE_INPUT Input )
		{
			VS_INDOMITA_GUI_FIRE_OUTPUT Out;

			float frameTime = GlobalTime / 70;
			float speed1 = frameTime * 0.95;
			float speed2 = frameTime * 0.9;
			float speed3 = frameTime * 0.85;
			float3 scrollSpeeds = float3(speed1, speed2, speed3);
			float3 scales = float3(1,2,3);
			float padding = 0.0f;

			// This part comes straight from VS_OUTPUT_PDX_GUI, it sets position for the gui elements correctly, I think
			float2 PixelPos = WidgetLeftTop + Input.LeftTop_WidthHeight.xy + Input.Position * Input.LeftTop_WidthHeight.zw;
			Out.Position = PixelToScreenSpace( PixelPos );
			Out.UV0 = Input.UVLeftTop_WidthHeight.xy + Input.Position * Input.UVLeftTop_WidthHeight.zw;
			Out.Color = Input.Color;
			// END VS_OUTPUT_PDX_GUI copy

		    // Compute texture coordinates for first noise texture using the first scale and upward scrolling speed values.
		    Out.texCoords1 = (Input.LeftTop_WidthHeight * scales.x);
		    Out.texCoords1.y = Out.texCoords1.y + (frameTime * scrollSpeeds.x);

		    // Compute texture coordinates for second noise texture using the second scale and upward scrolling speed values.
		    Out.texCoords2 = (Input.LeftTop_WidthHeight * scales.y);
		    Out.texCoords2.y = Out.texCoords2.y + (frameTime * scrollSpeeds.y);

		    // Compute texture coordinates for third noise texture using the third scale and upward scrolling speed values.
		    Out.texCoords3 = (Input.LeftTop_WidthHeight * scales.z);
		    Out.texCoords3.y = Out.texCoords3.y + (frameTime * scrollSpeeds.z);

			return Out;
		}
	]]
	
	MainCode VS_TiGuiFire
	{
		Input = "VS_INDOMITA_GUI_FIRE_INPUT"
		Output = "VS_INDOMITA_GUI_FIRE_OUTPUT"
		Code
		[[
			PDX_MAIN
			{
				return IndomitaGuiFireVertexShader( Input );
			}
		]]
	}
}


PixelShader =
{
	# The three textures for the fire effect are the fire color texture, the noise texture, and the alpha texture.
	
	TextureSampler FireTex
    {
        Index = 12
        MagFilter = "Linear"
		MinFilter = "Linear"
		MipFilter = "Linear"
		SampleModeU = "Wrap"
		SampleModeV = "Wrap"
        File = "gfx/fire/flame.dds"
    }

    TextureSampler NoiseTex
    {
    	Index = 13
    	MagFilter = "Linear"
    	MinFilter = "Linear"
    	MipFilter = "Linear"
    	SampleModeU = "Wrap"
    	SampleModeV = "Wrap"
    	File = "gfx/fire/flame_noise.dds"
    }

    TextureSampler AlphaTex
    {
    	Index = 14
    	MagFilter = "Linear"
    	MinFilter = "Linear"
    	MipFilter = "Linear"
    	SampleModeU = "Wrap"
    	SampleModeV = "Wrap"
    	File = "gfx/fire/flame_alpha.dds"
    }
    # These are resampled with Clamp because if they use Wrap the texture wraps wrong
	TextureSampler FireTex2
    {
        Index = 15
        MagFilter = "Linear"
		MinFilter = "Linear"
		MipFilter = "Linear"
		SampleModeU = "Clamp"
		SampleModeV = "Clamp"
        File = "gfx/fire/flame.dds"
    }

	TextureSampler AlphaTex2
    {
        Index = 16
        MagFilter = "Linear"
		MinFilter = "Linear"
		MipFilter = "Linear"
		SampleModeU = "Clamp"
		SampleModeV = "Clamp"
        File = "gfx/fire/flame_alpha.dds"
    }

    TextureSampler Texture
    {
    	Ref = PdxTexture0
    	MagFilter = "Point"
    	MinFilter = "Point"
    	MipFilter = "Point"
    	SampleModeU = "Clamp"
    	SampleModeV = "Clamp"
    }

	MainCode PS_TiGuiFire
	{	
		Input = "VS_INDOMITA_GUI_FIRE_OUTPUT"
		Output = "PDX_COLOR"
		Code
		[[
			PDX_MAIN
			{
				float4 noise1;
				float4 noise2;
				float4 noise3;
				float4 finalNoise;
				float perturb;
				float2 noiseCoords;
				float4 fireColor;
				float4 alphaColor;

				float2 distortion1 = float2(0.1f, 0.2f);
				float2 distortion2 = float2(0.1f, 0.3f);
				float2 distortion3 = float2(0.1f, 0.1f);
				float distortionScale = 0.1f;
				float distortionBias = 0.05f;

				// Sample the same noise texture using the three different texture coordinates to get three different noise scales.
				noise1 = PdxTex2D( FireTex, Input.texCoords1);
				noise2 = PdxTex2D( NoiseTex, Input.texCoords2);
				noise3 = PdxTex2D( AlphaTex, Input.texCoords3);

				// noise1 = PdxTex2D( FireTex, Input.UV0 );
				// noise2 = PdxTex2D( NoiseTex, Input.UV0 );
				// noise3 = PdxTex2D( AlphaTex, Input.UV0 );

				// Move the noise from the (0, 1) range to the (-1, +1) range.
				noise1 = (noise1 - 0.5f) * 2.0f;
				noise2 = (noise2 - 0.5f) * 2.0f;
				noise3 = (noise3 - 0.5f) * 2.0f;

				// Distort the three noise x and y coordinates by the three different distortion x and y values.
				noise1.xy = noise1.xy * distortion1.xy;
				noise2.xy = noise2.xy * distortion2.xy;
				noise3.xy = noise3.xy * distortion3.xy;

				// Combine all three distorted noise results into a single noise result.
				finalNoise = noise1 + noise2 + noise3;

				// Perturb the input texture Y coordinates by the distortion scale and bias values.  
				// The perturbation gets stronger as you move up the texture which creates the flame flickering at the top effect.
				perturb = ((1.0f - Input.UV0.y) * distortionScale) + distortionBias;

				// Now create the perturbed and distorted texture sampling coordinates that will be used to sample the fire color texture.
				noiseCoords.xy = (finalNoise.xy * perturb) + Input.UV0.xy;

				// Sample the color from the fire texture using the perturbed and distorted texture sampling coordinates.
				// Use the clamping sample state instead of the wrap sample state to prevent flames wrapping around.
				fireColor = PdxTex2D( FireTex2, noiseCoords.xy);
				

				// Sample the alpha value from the alpha texture using the perturbed and distorted texture sampling coordinates.
				// This will be used for transparency of the fire.
				// Use the clamping sample state instead of the wrap sample state to prevent flames wrapping around.
				alphaColor = PdxTex2D( AlphaTex2, noiseCoords.xy).a;

				// Set the alpha blending of the fire to the perturbed and distored alpha texture value.
				fireColor.a = alphaColor;

				float4 OutColor = SampleImageSprite( Texture, Input.UV0 );
				OutColor *= Input.Color;
				
				#ifdef DISABLED
					//float3 OutCross = cross(OutColor.rgb, fireColor.rgb);
					float OutAlpha = (OutColor.a * fireColor.a);
					//OutColor = float4(OutCross.r, OutCross.g, OutCross.b, OutAlpha);
					//OutColor = lerp(OutColor.rgb, fireColor.rgb, 0.1f);
					float3 OutCross = lerp(OutColor.rgb, fireColor.rgb, 0.9f );
					OutColor = float4(OutCross.r, OutCross.g, OutCross.b, OutAlpha);
					//OutColor = fireColor;
				#endif

				return OutColor;
			}
		]]
	}
}

BlendState BlendState
{
	BlendEnable = yes
	SourceBlend = "SRC_ALPHA"
	DestBlend = "INV_SRC_ALPHA"
}

BlendState BlendStateNoAlpha
{
	BlendEnable = no
}

BlendState PreMultipliedAlpha
{
	BlendEnable = yes
	SourceBlend = "ONE"
	DestBlend = "INV_SRC_ALPHA"
}

DepthStencilState DepthStencilState
{
	DepthEnable = no
}


Effect PdxGuiDefault
{
	VertexShader = "VS_TiGuiFire"
	PixelShader = "PS_TiGuiFire"
}
Effect PdxGuiDefaultDisabled
{
	VertexShader = "VS_TiGuiFire"
	PixelShader = "PS_TiGuiFire"
	
	Defines = { "DISABLED" }
}

Effect PdxGuiDefaultNoAlpha
{
	VertexShader = "VS_TiGuiFire"
	PixelShader = "PS_TiGuiFire"
	BlendState = BlendStateNoAlpha
}
Effect PdxGuiDefaultNoAlphaDisabled
{
	VertexShader = "VS_TiGuiFire"
	PixelShader = "PS_TiGuiFire"
	BlendState = BlendStateNoAlpha
	
	Defines = { "DISABLED" }
}

Effect PdxGuiPreMultipliedAlpha
{
	VertexShader = "VS_TiGuiFire"
	PixelShader = "PS_TiGuiFire"
	BlendState = PreMultipliedAlpha
}
Effect PdxGuiPreMultipliedAlphaDisabled
{
	VertexShader = "VS_TiGuiFire"
	PixelShader = "PS_TiGuiFire"
	BlendState = PreMultipliedAlpha
	
	Defines = { "DISABLED" }
}
