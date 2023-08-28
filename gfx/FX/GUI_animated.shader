# pdxgui_default.shader with a bunch of different effects
# Use effectname = "x" in the gui to use a different pixel shader for different gui widgets

Includes = {
	"cw/pdxgui.fxh"
	"cw/pdxgui_sprite.fxh"
	"standardfuncsgfx.fxh"
	# standardfuncsgfx.fxh imported for GlobalTime
	# If using in Victoria 3 change to "sharedconstants.fxh"
	# If using in CK3 or Imperator keep "standardfuncsgfx.fxh"
}

VertexShader =
{
	MainCode VS_Default
	{
		Input = "VS_INPUT_PDX_GUI"
		Output = "VS_OUTPUT_PDX_GUI"
		Code
		[[
			PDX_MAIN
			{
				return PdxGuiDefaultVertexShader( Input );
			}
		]]
	}
}

PixelShader =
{
	TextureSampler Texture
	{
		Ref = PdxTexture0
		MagFilter = "Point"
		MinFilter = "Point"
		MipFilter = "Point"
		SampleModeU = "Clamp"
		SampleModeV = "Clamp"
	}
	MainCode PS_Default
	{	
		Input = "VS_OUTPUT_PDX_GUI"
		Output = "PDX_COLOR"
		Code
		[[
			PDX_MAIN
			{
				float4 OutColor = SampleImageSprite( Texture, Input.UV0 );
				OutColor *= Input.Color;
				
				#ifdef DISABLED
					OutColor.rgb = DisableColor( OutColor.rgb );
				#endif
				
			    return OutColor;
			}
		]]
	}
	MainCode PS_StormyNight
	{	
		Input = "VS_OUTPUT_PDX_GUI"
		Output = "PDX_COLOR"
		Code
		[[
			float rand(float2 p){
				p+=.2127+p.x+.3713*p.y;
				float2 r=4.789*sin(789.123*(p));
				return frac(r.x*r.y);
			}
			float sn(float2 p){
				float2 i=floor(p-.5);
				float2 f=frac(p-.5);
				f = f*f*f*(f*(f*6.0-15.0)+10.0);
				float rt=lerp(rand(i),rand(i+float2(1.,0.)),f.x);
				float rb=lerp(rand(i+float2(0.,1.)),rand(i+float2(1.,1.)),f.x);
				return lerp(rt,rb,f.y);
			}
			PDX_MAIN
			{
				// https://www.shadertoy.com/view/XsX3DS
				float iTime = GlobalTime * 0.4;
				float2 uv = Input.UV0 + 0.19;

				float2 p = uv.xy*float2(3.,4.3);
				float f = .5*sn(p)+.25*sn(2.*p)+.125*sn(4.*p)+.0625*sn(8.*p)+.03125*sn(16.*p)+.015*sn(32.*p);
				
				float newT = iTime * 0.4 + sn(vec2(iTime*1.0))*0.1;
				p.x-=iTime*0.2;
				
				p.y*=1.3;
				float f2 = .5*sn(p)+.25*sn(2.04*p+newT*1.1)-.125*sn(4.03*p-iTime*0.3)+.0625*sn(8.02*p-iTime*0.4)+.03125*sn(16.01*p+iTime*0.5)+.018*sn(24.02*p);
				
				float f3 = .5*sn(p)+.25*sn(2.04*p+newT*1.1)-.125*sn(4.03*p-iTime*0.3)+.0625*sn(8.02*p-iTime*0.5)+.03125*sn(16.01*p+iTime*0.6)+.019*sn(18.02*p);
				
				float f4 = f2 * smoothstep(0.0,1.0,uv.y);
				
				float3 clouds = lerp(float3(-0.4,-0.4,-0.15),float3(1.4,1.4,1.3),f4*f);
				float lightning = sn((f3)+float(pow(sn(vec2(iTime*4.5)),6.)));

				lightning *= smoothstep(0.0,1.,uv.y+0.5);

				lightning = smoothstep(0.76,1.,lightning);
				lightning=lightning*2.;
				
				float2 moonp = float2(0.7,0.4);
				float moon = smoothstep(0.95,0.956,1.0-length(uv-moonp));
				float2 moonp2 = moonp + float2(0.015, 0);
				moon -= smoothstep(0.93,0.956,1.-length(uv-moonp2));
				moon = clamp(moon, 0., 1.);
				moon += 0.3*smoothstep(0.80,0.956,1.-length(uv-moonp));

				clouds+= pow(1.-length(uv-moonp),1.2)*0.4;

				clouds*=0.8;
				clouds += lightning + moon +0.2;

				float2 newUV = uv;
				newUV.x+=iTime*0.3;
				newUV.y-=iTime*3.;
				float strength = sin(iTime*0.5+sn(newUV))*0.05+0.05;
				
				float rain = sn( float2(newUV.x*20.1, newUV.y*40.1+newUV.x*400.1-20.*strength ));
				float rain2 = sn( float2(newUV.x*45.+iTime*0.5, newUV.y*30.1+newUV.x*200.1 ));	
				rain = strength-rain;
				rain+=smoothstep(0.2,0.5,f4+lightning+0.1)*rain;
				rain += pow(length(uv-moonp),1.)*0.1;
				rain+=rain2*(sin(strength)-0.4)*2.;
				rain = clamp(rain, 0.,0.5)*0.5;
				
				float3 painting = (clouds + rain)+clamp(rain*(strength-0.1),0.,1.);
				
				float r=1.-length(max(abs(Input.UV0.xy*2.-1.)-.5,0.)); 
				painting*=r;
			    return float4(painting, 1.0);
			}
		]]
	}
	MainCode PS_BigBang
	{	
		Input = "VS_OUTPUT_PDX_GUI"
		Output = "PDX_COLOR"
		Code
		[[
			PDX_MAIN
			{
				// https://www.shadertoy.com/view/MdXSzS
				float2 uv = Input.UV0 - .5;
				float t = GlobalTime * .05 + ((.25 + .05 * sin(GlobalTime * .1))/(length(uv.xy) + .07)) * 2.2;
				float si = sin(t);
				float co = cos(t);
				float2x2 ma = Create2x2(co, si, -si, co);

				float v1 = 0.0;
				float v2 = 0.0;
				float v3 = 0.0;
				float s = 0.0;
				for (int i = 0; i < 60; i++)
				{
				    float3 p = s * float3(uv, 0.0);
				    p.xy = mul(ma, p.xy);
				    p += float3(.22, .3, s - 1.5 - sin(GlobalTime * .13) * .1);
				    for (int i = 0; i < 8; i++) p = abs(p) / dot(p,p) - 0.659;
				    v1 += dot(p,p) * .0015 * (1.8 + sin(length(uv.xy * 13.0) + .5  - GlobalTime * .2));
				    v2 += dot(p,p) * .0013 * (1.5 + sin(length(uv.xy * 14.5) + 1.2 - GlobalTime * .3));
				    v3 += length(p.xy*10.) * .0003;
				    s  += .035;
				}
				
				float len = length(uv);
				v1 *= smoothstep(.7, .0, len);
				v2 *= smoothstep(.5, .0, len);
				v3 *= smoothstep(.9, .0, len);
				
				float3 col = float3( v3 * (1.5 + sin(GlobalTime * .2) * .4),
				                (v1 + v3) * .3,
				                 v2) + smoothstep(0.2, .0, len) * .85 + smoothstep(.0, .6, v3) * .3;

				float4 fragColor=float4(min(pow(abs(col), vec3(1.2)), 1.0), 1.0);
				
			    return fragColor;
			}
		]]
	}
	MainCode PS_CloudCover
	{	
		Input = "VS_OUTPUT_PDX_GUI"
		Output = "PDX_COLOR"
		Code
		[[
			// https://www.shadertoy.com/view/WdXBW4

			static const float cloudscale = 1.1;
			static const float speed = 0.009;
			static const float clouddark = 0.5;
			static const float cloudlight = 0.3;
			static const float cloudcover = 0.2;
			static const float cloudalpha = 8.0;
			static const float skytint = 0.4;
			static const float3 skycolour1 = float3(0.0, 0.0, 0.0);
			static const float3 skycolour2 = float3(0.4, 0.7, 1.0);
			static const float2x2 m = Create2x2( 1.6,  1.2, -1.2,  1.6 );

			float2 hash( float2 p ) {
				p = float2(dot(p,float2(127.1,311.7)), dot(p,float2(269.5,183.3)));
				return -1.0 + 2.0*frac(sin(p)*43758.5453123);
			}

			float get_noise( in float2 p ) {
			    static const float K1 = 0.366025404; // (sqrt(3)-1)/2;
			    static const float K2 = 0.211324865; // (3-sqrt(3))/6;
				float2 i = floor(p + (p.x+p.y)*K1);	
			    float2 a = p - i + (i.x+i.y)*K2;
			    float2 o = (a.x>a.y) ? float2(1.0,0.0) : float2(0.0,1.0);
			    float2 b = a - o + K2;
				float2 c = a - 1.0 + 2.0*K2;
			    float3 h = max(0.5-float3(dot(a,a), dot(b,b), dot(c,c) ), 0.0 );
				float3 n = h*h*h*h*float3( dot(a,hash(i+0.0)), dot(b,hash(i+o)), dot(c,hash(i+1.0)));
			    return dot(n, vec3(70.0));	
			}

			float fbm(float2 n) {
				float total = 0.0;
				float amplitude = 0.1;
				for (int i = 0; i < 7; i++) {
					total += get_noise(n) * amplitude;
					n = mul(m, n);
					amplitude *= 0.4;
				}
				return total;
			}
			PDX_MAIN
			{
				float2 uv = Input.UV0;
			    float time = GlobalTime * speed;
			    float q = fbm(uv * cloudscale * 0.51);
			    
			    //ridged noise shape
				float r = 0.0;
				uv *= cloudscale;
			    uv -= q - time;
			    float weight = 0.8;
			    for (int i=0; i<8; i++){
					r += abs(weight*get_noise( uv ));
			        uv = mul(m, uv) + time;
					weight *= 0.7;
			    }
			    
			    //noise shape
				float f = 0.0;
			    uv = Input.UV0;
				uv *= cloudscale;
			    uv -= q - time;
			    weight = 0.7;
			    for (int j=0; j<8; j++){
					f += weight*get_noise( uv );
			        uv = mul(m, uv) + time;
					weight *= 0.6;
			    }
			    
			    f *= r + f;
			    
			    //noise colour
			    float c = 0.0;
			    time = GlobalTime * speed * 2.0;
			    uv = Input.UV0;
				uv *= cloudscale*2.0;
			    uv -= q - time;
			    weight = 0.4;
			    for (int k=0; k<7; k++){
					c += weight*get_noise( uv );
			        uv = mul(m, uv) + time;
					weight *= 0.6;
			    }
			    
			    //noise ridge colour
			    float c1 = 0.0;
			    time = GlobalTime * speed * 3.0;
			    uv = Input.UV0;
				uv *= cloudscale*3.0;
			    uv -= q - time;
			    weight = 0.4;
			    for (int l=0; l<7; l++){
					c1 += abs(weight*get_noise( uv ));
			        uv = mul(m, uv) + time;
					weight *= 0.6;
			    }
				
			    c += c1;
			    
			    float3 skycolour = lerp(skycolour1, skycolour2, Input.UV0.y-0.1);
			    float3 cloudcolour = float3(1.1, 1.1, 0.9) * clamp((clouddark + cloudlight*c), 0.0, 1.0);
			   
			    f = cloudcover + cloudalpha*f*r;
			    //skycolour += pow(abs(get_noise((uv) * 0.1)), 15.) * 5.0 * Input.UV0.y;
			    float3 result = lerp(skycolour, clamp(skytint * skycolour + cloudcolour, 0.0, 1.0), clamp(f + c, 0.0, 1.0));
			    
				float4 OutColor = float4( result, 1.0 );

			    return OutColor;
			}
		]]
	}
	MainCode PS_StarField
	{	
		Input = "VS_OUTPUT_PDX_GUI"
		Output = "PDX_COLOR"
		Code
		[[
			PDX_MAIN
			{
				// https://www.shadertoy.com/view/XlfGRj
				#define iterations 17
				#define formuparam 0.64

				#define volsteps 20
				#define stepsize 0.125

				#define zoom   1.200
				#define tile   0.850
				#define speed  0.01

				#define brightness 0.0004
				#define darkmatter 0.400
				#define distfading 0.730
				#define saturation 0.950

				//get coords and direction
				float2 uv=Input.UV0;
				float3 dir=float3(uv*zoom,1.);
				float time=GlobalTime*speed+.25;
				time *= 0.001;
				//mouse rotation
				//float a1=.5+Input.UV0.x*2.;
				//float a2=.8+Input.UV0.y*2.;
				//float2x2 rot1=Create2x2(cos(a1),sin(a1),-sin(a1),cos(a1));
				//float2x2 rot2=Create2x2(cos(a2),sin(a2),-sin(a2),cos(a2));
				//dir.xz = mul(rot1, dir.xz);
				//dir.xz = mul(rot2, dir.xz);
				float3 from=float3(1.,.5,0.5);
				from+=float3(time*2.,time,-2.);
				//dir.xz = mul(rot1, from.xz);
				//dir.xz = mul(rot2, from.xz);

				//volumetric rendering
				float s=0.1,fade=0.4;
				float3 v=vec3(0.);
				for (int r=0; r<volsteps; r++) {
					float3 p=from+s*dir*.5;
					p = abs(vec3(tile)-mod(p,vec3(tile*2.))); // tiling fold
					float pa,a=pa=0.;
					for (int i=0; i<iterations; i++) { 
						p=abs(p)/dot(p,p)-formuparam; // the magic formula
						a+=abs(length(p)-pa); // absolute sum of average change
						pa=length(p);
					}
					float dm=max(0.,darkmatter-a*a*.001); //dark matter
					a*=a*a; // add contrast
					if (r>6) fade*=1.-dm; // dark matter, don't render near
					//v+=vec3(dm,dm*.5,0.);
					v+=fade;
					v+=float3(s,s*s,s*s*s*s)*a*brightness*fade; // coloring based on distance
					fade*=distfading; // distance fading
					s+=stepsize;
				}
				v=lerp(vec3(length(v)),v,saturation); //color adjust
				return float4(v*.01,1.0);
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
	VertexShader = "VS_Default"
	PixelShader = "PS_Default"
}
Effect PdxGuiDefaultDisabled
{
	VertexShader = "VS_Default"
	PixelShader = "PS_Default"
	
	Defines = { "DISABLED" }
}

Effect PdxGuiDefaultNoAlpha
{
	VertexShader = "VS_Default"
	PixelShader = "PS_Default"
	BlendState = BlendStateNoAlpha
}
Effect PdxGuiDefaultNoAlphaDisabled
{
	VertexShader = "VS_Default"
	PixelShader = "PS_Default"
	BlendState = BlendStateNoAlpha
	
	Defines = { "DISABLED" }
}

Effect PdxGuiPreMultipliedAlpha
{
	VertexShader = "VS_Default"
	PixelShader = "PS_Default"
	BlendState = PreMultipliedAlpha
}
Effect PdxGuiPreMultipliedAlphaDisabled
{
	VertexShader = "VS_Default"
	PixelShader = "PS_Default"
	BlendState = PreMultipliedAlpha
	
	Defines = { "DISABLED" }
}

Effect StormyNight
{
	VertexShader = "VS_Default"
	PixelShader = "PS_StormyNight"
}
Effect StormyNightDisabled
{
	VertexShader = "VS_Default"
	PixelShader = "PS_StormyNight"
	
	Defines = { "DISABLED" }
}

Effect BigBang
{
	VertexShader = "VS_Default"
	PixelShader = "PS_BigBang"
}
Effect BigBangDisabled
{
	VertexShader = "VS_Default"
	PixelShader = "PS_BigBang"
	
	Defines = { "DISABLED" }
}

Effect CloudCover
{
	VertexShader = "VS_Default"
	PixelShader = "PS_CloudCover"
}
Effect CloudCoverDisabled
{
	VertexShader = "VS_Default"
	PixelShader = "PS_CloudCover"
	
	Defines = { "DISABLED" }
}

Effect StarField
{
	VertexShader = "VS_Default"
	PixelShader = "PS_StarField"
}
Effect StarFieldDisabled
{
	VertexShader = "VS_Default"
	PixelShader = "PS_StarField"
	
	Defines = { "DISABLED" }
}
