Includes = {
	"terra_incognita.fxh"
}

PixelShader =
{
	Samplers =
	{
		# HW - Start
		#CenterTexture =
		#{
		#	Index = 0;
		#	MagFilter = "Linear";
		#	MinFilter = "Linear";
		#	AddressU = "Wrap";
		#	AddressV = "Wrap";
		#}
		# HW - End
		TerraIncognitaTexture =
		{
			Index = 1;
			MagFilter = "Linear";
			MinFilter = "Linear";
			AddressU = "Clamp"
			AddressV = "Clamp"
		}
	}
}

VertexStruct VS_INPUT
{
    float2 vPosition  		: POSITION;
	float2 vUV				: TEXCOORD0;
};

VertexStruct VS_OUTPUT
{
    float4 vPosition 	: PDX_POSITION;
	float2 vUV			: TEXCOORD0;
	float4 vPos			: TEXCOORD1;
};

ConstantBuffer( Common, 0, 0 )
{
	float4x4 	ViewProjectionMatrix;
};


VertexShader =
{
	MainCode VertexShader
		ConstantBuffers = { Common }
	[[
		VS_OUTPUT main(const VS_INPUT v )
		{
			VS_OUTPUT Out;
			float4 vPos = float4( v.vPosition.x, -1.5f, v.vPosition.y, 1.0f );
			vPos.xz *= 1.5f; //Increase size slightly

			Out.vPos = vPos;
			Out.vPosition  	= mul( ViewProjectionMatrix, vPos );
			Out.vUV			= v.vUV;
			return Out;
		}

	]]
}

PixelShader =
{
	MainCode PixelShader
	[[
		float4 main( VS_OUTPUT v ) : PDX_COLOR
		{
			#float4 vColor = tex2D( CenterTexture, v.vUV );  # HW
			vColor = ApplyTerraIncognita( vColor, v.vPos.xz, 1.f, TerraIncognitaTexture );
			return vColor;
		}

	]]
}


DepthStencilState DepthStencilState
{
	DepthEnable = no
}

BlendState BlendState
{
	BlendEnable = yes
	AlphaTest = no
	SourceBlend = "ONE"
	DestBlend = "ONE"
}

RasterizerState RasterizerState
{
	FillMode = "FILL_SOLID";
	CullMode = "CULL_BACK";
	FrontCCW = no
}


Effect GalaxyCenter
{
	VertexShader = "VertexShader";
	PixelShader = "PixelShader";
}
