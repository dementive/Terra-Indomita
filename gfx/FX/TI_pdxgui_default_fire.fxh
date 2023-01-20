Includes = {
	"standardfuncsgfx.fxh"
}

VertexShader =
{		
	Code
	[[
		#define FRAME_TIME GlobalTime / 70.0
		#define SCROLL_SPEEDS float3(FRAME_TIME * 0.95, FRAME_TIME * 0.9, FRAME_TIME * 0.85)
		#define SCALES float3(1,2,3)
		#define PADDING 0.0f
	]]
}

PixelShader =
{		
	Code
	[[
		#define DISTORTION1 float2(0.1f, 0.2f)
		#define DISTORTION2 float2(0.1f, 0.3f)
		#define DISTORTION3 float2(0.1f, 0.1f)
		#define DISTORTION_SCALE 0.1f
		#define DISTORTION_BIAS 0.05f
	]]
}
