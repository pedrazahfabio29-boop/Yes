from flask import Flask, request, jsonify
import requests
import uuid
import os
import re
from xml.sax.saxutils import escape as xml_escape

app = Flask(__name__)

# =========================================================
# HARD-CODED REAL TEMPLATE
# Paste your full rbxlx template here exactly once.
# Keep it raw inside triple quotes.
# =========================================================
TEMPLATE = r"""<roblox xmlns:xmime="http://www.w3.org/2005/05/xmlmime" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://www.roblox.com/roblox.xsd" version="4">
	<External>null</External>
	<External>nil</External>
	<Item class="Workspace" referent="RBXB781519A068442EAB4447566E5E6E980">
		<Properties>
			<float name="AirDensity">0.00120000006</float>
			<float name="AirTurbulenceIntensity">0</float>
			<bool name="AllowThirdPartySales">false</bool>
			<token name="AuthorityMode">1</token>
			<token name="AvatarUnificationMode">0</token>
			<token name="ClientAnimatorThrottling">0</token>
			<BinaryString name="CollisionGroupData">AQEABP////8HRGVmYXVsdA==</BinaryString>
			<Ref name="CurrentCamera">RBX2F9BFB1BE9344528BF07AD8FDF8D6E5A</Ref>
			<double name="DistributedGameTime">0</double>
			<token name="EnableSLIMAvatars">0</token>
			<bool name="ExplicitAutoJoints">true</bool>
			<bool name="FallHeightEnabled">true</bool>
			<float name="FallenPartsDestroyHeight">-500</float>
			<token name="FluidForces">0</token>
			<Vector3 name="GlobalWind">
				<X>0</X>
				<Y>0</Y>
				<Z>0</Z>
			</Vector3>
			<float name="Gravity">196.199997</float>
			<token name="IKControlConstraintSupport">0</token>
			<token name="LayeredClothingCacheOptimizations">0</token>
			<token name="LuauTypeCheckMode">0</token>
			<token name="MeshPartHeadsAndAccessories">0</token>
			<token name="ModelStreamingBehavior">0</token>
			<token name="MoverConstraintRootBehavior">0</token>
			<token name="NextGenerationReplication">0</token>
			<token name="PathfindingUseImprovedSearch">0</token>
			<token name="PhysicsImprovedSleep">0</token>
			<token name="PhysicsSteppingMethod">0</token>
			<token name="PlayerCharacterDestroyBehavior">0</token>
			<token name="PlayerScriptsUseInputActionSystem">0</token>
			<token name="PrimalPhysicsSolver">0</token>
			<token name="RejectCharacterDeletions">0</token>
			<token name="RenderingCacheOptimizations">0</token>
			<token name="ReplicateInstanceDestroySetting">0</token>
			<token name="Retargeting">0</token>
			<token name="SandboxedInstanceMode">0</token>
			<token name="SignalBehavior2">2</token>
			<token name="StreamOutBehavior">2</token>
			<bool name="StreamingEnabled">true</bool>
			<token name="StreamingIntegrityMode">3</token>
			<int name="StreamingMinRadius">64</int>
			<int name="StreamingTargetRadius">1024</int>
			<bool name="TerrainWeldsFixed">true</bool>
			<token name="TouchEventsUseCollisionGroups">0</token>
			<bool name="TouchesUseCollisionGroups">false</bool>
			<token name="UseFixedSimulation">0</token>
			<token name="UseNewLuauTypeSolver">2</token>
			<token name="LevelOfDetail">0</token>
			<CoordinateFrame name="ModelMeshCFrame">
				<X>0</X>
				<Y>0</Y>
				<Z>0</Z>
				<R00>1</R00>
				<R01>0</R01>
				<R02>0</R02>
				<R10>0</R10>
				<R11>1</R11>
				<R12>0</R12>
				<R20>0</R20>
				<R21>0</R21>
				<R22>1</R22>
			</CoordinateFrame>
			<SharedString name="ModelMeshData">yuZpQdnvvUBOTYh1jqZ2cA==</SharedString>
			<Vector3 name="ModelMeshSize">
				<X>0</X>
				<Y>0</Y>
				<Z>0</Z>
			</Vector3>
			<token name="ModelStreamingMode">0</token>
			<bool name="NeedsPivotMigration">false</bool>
			<Ref name="PrimaryPart">null</Ref>
			<float name="ScaleFactor">1</float>
			<SharedString name="SlimHash">yuZpQdnvvUBOTYh1jqZ2cA==</SharedString>
			<OptionalCoordinateFrame name="WorldPivotData">
				<CFrame>
					<X>0</X>
					<Y>0</Y>
					<Z>0</Z>
					<R00>1</R00>
					<R01>0</R01>
					<R02>0</R02>
					<R10>0</R10>
					<R11>1</R11>
					<R12>0</R12>
					<R20>0</R20>
					<R21>0</R21>
					<R22>1</R22>
				</CFrame>
			</OptionalCoordinateFrame>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">Workspace</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b00000002</UniqueId>
		</Properties>
		<Item class="Camera" referent="RBX2F9BFB1BE9344528BF07AD8FDF8D6E5A">
			<Properties>
				<CoordinateFrame name="CFrame">
					<X>-19.6960945</X>
					<Y>14.0916243</Y>
					<Z>-19.3038864</Z>
					<R00>-0.706150889</R00>
					<R01>0.31296584</R01>
					<R02>-0.635140479</R02>
					<R10>-8.39972536e-09</R10>
					<R11>0.897013366</R11>
					<R12>0.442003787</R12>
					<R20>0.708061457</R20>
					<R21>0.312121361</R21>
					<R22>-0.633426726</R22>
				</CoordinateFrame>
				<Ref name="CameraSubject">null</Ref>
				<token name="CameraType">0</token>
				<float name="FieldOfView">70</float>
				<token name="FieldOfViewMode">0</token>
				<CoordinateFrame name="Focus">
					<X>-18.4258137</X>
					<Y>13.2076168</Y>
					<Z>-18.0370331</Z>
					<R00>1</R00>
					<R01>0</R01>
					<R02>0</R02>
					<R10>0</R10>
					<R11>1</R11>
					<R12>0</R12>
					<R20>0</R20>
					<R21>0</R21>
					<R22>1</R22>
				</CoordinateFrame>
				<bool name="HeadLocked">true</bool>
				<float name="HeadScale">1</float>
				<bool name="VRTiltAndRollEnabled">false</bool>
				<BinaryString name="AttributesSerialize"></BinaryString>
				<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
				<bool name="DefinesCapabilities">false</bool>
				<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
				<string name="Name">Camera</string>
				<int64 name="SourceAssetId">-1</int64>
				<BinaryString name="Tags"></BinaryString>
				<UniqueId name="UniqueId">1bdada4610e5816909da199b000003a7</UniqueId>
			</Properties>
		</Item>
		<Item class="Terrain" referent="RBX2885E644536D465DB7EECF9D3EF81591">
			<Properties>
				<token name="AcquisitionMethod">0</token>
				<bool name="Decoration">true</bool>
				<float name="GrassLength">0.699999988</float>
				<BinaryString name="MaterialColors"><![CDATA[AAAAAAAAb34+WFlWmJiYimFJz8unrJRsY2Rm3eTl6/3/lHxfeXBiS0pKjIJo/xhDUFRUhoZ2
zNLfaoZA///+//PAj5CH]]></BinaryString>
				<BinaryString name="PhysicsGrid">AgMAAAAAAAAAAAAAAAA=</BinaryString>
				<BinaryString name="SmoothGrid">AQU=</BinaryString>
				<bool name="SmoothVoxelsUpgraded">false</bool>
				<Color3 name="WaterColor">
					<R>0.0470588282</R>
					<G>0.329411775</G>
					<B>0.360784322</B>
				</Color3>
				<float name="WaterReflectance">1</float>
				<float name="WaterTransparency">0.300000012</float>
				<float name="WaterWaveSize">0.150000006</float>
				<float name="WaterWaveSpeed">10</float>
				<bool name="Anchored">true</bool>
				<bool name="AudioCanCollide">true</bool>
				<float name="BackParamA">-0.5</float>
				<float name="BackParamB">0.5</float>
				<token name="BackSurface">0</token>
				<token name="BackSurfaceInput">0</token>
				<float name="BottomParamA">-0.5</float>
				<float name="BottomParamB">0.5</float>
				<token name="BottomSurface">4</token>
				<token name="BottomSurfaceInput">0</token>
				<CoordinateFrame name="CFrame">
					<X>0</X>
					<Y>0</Y>
					<Z>0</Z>
					<R00>1</R00>
					<R01>0</R01>
					<R02>0</R02>
					<R10>0</R10>
					<R11>1</R11>
					<R12>0</R12>
					<R20>0</R20>
					<R21>0</R21>
					<R22>1</R22>
				</CoordinateFrame>
				<bool name="CanCollide">true</bool>
				<bool name="CanQuery">true</bool>
				<bool name="CanTouch">true</bool>
				<bool name="CastShadow">true</bool>
				<string name="CollisionGroup">Default</string>
				<int name="CollisionGroupId">0</int>
				<Color3uint8 name="Color3uint8">4288914085</Color3uint8>
				<PhysicalProperties name="CustomPhysicalProperties">
					<CustomPhysics>false</CustomPhysics>
				</PhysicalProperties>
				<bool name="EnableFluidForces">true</bool>
				<float name="FrontParamA">-0.5</float>
				<float name="FrontParamB">0.5</float>
				<token name="FrontSurface">0</token>
				<token name="FrontSurfaceInput">0</token>
				<float name="LeftParamA">-0.5</float>
				<float name="LeftParamB">0.5</float>
				<token name="LeftSurface">0</token>
				<token name="LeftSurfaceInput">0</token>
				<bool name="Locked">true</bool>
				<bool name="Massless">false</bool>
				<token name="Material">256</token>
				<string name="MaterialVariantSerialized"></string>
				<CoordinateFrame name="PivotOffset">
					<X>0</X>
					<Y>0</Y>
					<Z>0</Z>
					<R00>1</R00>
					<R01>0</R01>
					<R02>0</R02>
					<R10>0</R10>
					<R11>1</R11>
					<R12>0</R12>
					<R20>0</R20>
					<R21>0</R21>
					<R22>1</R22>
				</CoordinateFrame>
				<float name="Reflectance">0</float>
				<float name="RightParamA">-0.5</float>
				<float name="RightParamB">0.5</float>
				<token name="RightSurface">0</token>
				<token name="RightSurfaceInput">0</token>
				<int name="RootPriority">0</int>
				<Vector3 name="RotVelocity">
					<X>0</X>
					<Y>0</Y>
					<Z>0</Z>
				</Vector3>
				<float name="TopParamA">-0.5</float>
				<float name="TopParamB">0.5</float>
				<token name="TopSurface">3</token>
				<token name="TopSurfaceInput">0</token>
				<float name="Transparency">0</float>
				<Vector3 name="Velocity">
					<X>0</X>
					<Y>0</Y>
					<Z>0</Z>
				</Vector3>
				<Vector3 name="size">
					<X>2044</X>
					<Y>252</Y>
					<Z>2044</Z>
				</Vector3>
				<BinaryString name="AttributesSerialize"></BinaryString>
				<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
				<bool name="DefinesCapabilities">false</bool>
				<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
				<string name="Name">Terrain</string>
				<int64 name="SourceAssetId">-1</int64>
				<BinaryString name="Tags"></BinaryString>
				<UniqueId name="UniqueId">1bdada4610e5816909da199b000003aa</UniqueId>
			</Properties>
		</Item>
	</Item>
	<Item class="TimerService" referent="RBX02B4D1C2C7FE416CB8607EA04BC7BBE4">
		<Properties>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">Instance</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b00000333</UniqueId>
		</Properties>
	</Item>
	<Item class="SoundService" referent="RBXF89EA0ECCF524C21A42E4DA8035D44F4">
		<Properties>
			<bool name="AcousticSimulationEnabled">false</bool>
			<token name="AmbientReverb">0</token>
			<token name="AudioApiByDefault">0</token>
			<token name="CharacterSoundsUseNewApi">0</token>
			<token name="DefaultListenerLocation">3</token>
			<float name="DistanceFactor">3.32999992</float>
			<float name="DopplerScale">1</float>
			<bool name="IsNewExpForAudioApiByDefault">false</bool>
			<bool name="RespectFilteringEnabled">true</bool>
			<float name="RolloffScale">1</float>
			<token name="VolumetricAudio">1</token>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">SoundService</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b00000334</UniqueId>
		</Properties>
	</Item>
	<Item class="VideoCaptureService" referent="RBX0A1245477F594376A2F0C325F0E9CF4D">
		<Properties>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">VideoCaptureService</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b00000340</UniqueId>
		</Properties>
	</Item>
	<Item class="NonReplicatedCSGDictionaryService" referent="RBX96B7CF1D1D3D48BFACBAA61336AA6388">
		<Properties>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">NonReplicatedCSGDictionaryService</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b00000341</UniqueId>
		</Properties>
	</Item>
	<Item class="CSGDictionaryService" referent="RBX38C15916DC404D93AA5F5B19631CD6AB">
		<Properties>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">CSGDictionaryService</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b00000342</UniqueId>
		</Properties>
	</Item>
	<Item class="Chat" referent="RBXCF1FD3D6D276443383372CBE00B994A6">
		<Properties>
			<bool name="BubbleChatEnabled">true</bool>
			<bool name="IsAutoMigrated">false</bool>
			<bool name="LoadDefaultChat">true</bool>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">Chat</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b00000348</UniqueId>
		</Properties>
	</Item>
	<Item class="Players" referent="RBX2A624CECABE942F8A9C42FC0F33E883F">
		<Properties>
			<bool name="BanningEnabled">true</bool>
			<bool name="CharacterAutoLoads">true</bool>
			<int name="MaxPlayersInternal">30</int>
			<int name="PreferredPlayersInternal">30</int>
			<float name="RespawnTime">3</float>
			<bool name="UseStrafingAnimations">false</bool>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">Players</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b0000034a</UniqueId>
		</Properties>
	</Item>
	<Item class="ReplicatedFirst" referent="RBX82CDFF8BBC3841B7B5ABCEE7F546D80E">
		<Properties>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">ReplicatedFirst</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b0000034d</UniqueId>
		</Properties>
	</Item>
	<Item class="TweenService" referent="RBX10E59E818B9B44769CEE1C464968804A">
		<Properties>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">TweenService</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b0000034f</UniqueId>
		</Properties>
	</Item>
	<Item class="MaterialService" referent="RBX97989034E09B4F3F8FDB8994EA968801">
		<Properties>
			<string name="AsphaltName">Asphalt</string>
			<string name="BasaltName">Basalt</string>
			<string name="BrickName">Brick</string>
			<string name="CardboardName">Cardboard</string>
			<string name="CarpetName">Carpet</string>
			<string name="CeramicTilesName">CeramicTiles</string>
			<string name="ClayRoofTilesName">ClayRoofTiles</string>
			<string name="CobblestoneName">Cobblestone</string>
			<string name="ConcreteName">Concrete</string>
			<string name="CorrodedMetalName">CorrodedMetal</string>
			<string name="CrackedLavaName">CrackedLava</string>
			<string name="DiamondPlateName">DiamondPlate</string>
			<string name="FabricName">Fabric</string>
			<string name="FoilName">Foil</string>
			<string name="GlacierName">Glacier</string>
			<string name="GraniteName">Granite</string>
			<string name="GrassName">Grass</string>
			<string name="GroundName">Ground</string>
			<string name="IceName">Ice</string>
			<string name="LeafyGrassName">LeafyGrass</string>
			<string name="LeatherName">Leather</string>
			<string name="LimestoneName">Limestone</string>
			<string name="MarbleName">Marble</string>
			<string name="MetalName">Metal</string>
			<string name="MudName">Mud</string>
			<string name="PavementName">Pavement</string>
			<string name="PebbleName">Pebble</string>
			<string name="PlasterName">Plaster</string>
			<string name="PlasticName">Plastic</string>
			<string name="RockName">Rock</string>
			<string name="RoofShinglesName">RoofShingles</string>
			<string name="RubberName">Rubber</string>
			<string name="SaltName">Salt</string>
			<string name="SandName">Sand</string>
			<string name="SandstoneName">Sandstone</string>
			<string name="SlateName">Slate</string>
			<string name="SmoothPlasticName">SmoothPlastic</string>
			<string name="SnowName">Snow</string>
			<bool name="Use2022MaterialsXml">true</bool>
			<string name="WoodName">Wood</string>
			<string name="WoodPlanksName">WoodPlanks</string>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">MaterialService</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b00000350</UniqueId>
		</Properties>
	</Item>
	<Item class="TextChatService" referent="RBX0EFA4F2D9DA84FA99638DC62C44D8ABA">
		<Properties>
			<bool name="ChatTranslationFTUXShown">true</bool>
			<bool name="ChatTranslationToggleEnabled">false</bool>
			<token name="ChatVersion">1</token>
			<bool name="CreateDefaultCommands">true</bool>
			<bool name="CreateDefaultTextChannels">true</bool>
			<bool name="HasSeenDeprecationDialog">false</bool>
			<bool name="IsLegacyChatDisabled">true</bool>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">TextChatService</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b00000351</UniqueId>
		</Properties>
		<Item class="ChatWindowConfiguration" referent="RBXBAFF6F0A2A644AB887DE325D7CCBB7BA">
			<Properties>
				<Color3 name="BackgroundColor3">
					<R>0.0980392173</R>
					<G>0.105882354</G>
					<B>0.113725491</B>
				</Color3>
				<double name="BackgroundTransparency">0.2999999999999999889</double>
				<bool name="Enabled">true</bool>
				<Font name="FontFace">
					<Family><url>rbxasset://fonts/families/BuilderSans.json</url></Family>
					<Weight>500</Weight>
					<Style>Normal</Style>
					<CachedFaceId><url>rbxasset://fonts/BuilderSans-Medium.otf</url></CachedFaceId>
				</Font>
				<float name="HeightScale">1</float>
				<token name="HorizontalAlignment">1</token>
				<Color3 name="TextColor3">
					<R>1</R>
					<G>1</G>
					<B>1</B>
				</Color3>
				<int64 name="TextSize">18</int64>
				<Color3 name="TextStrokeColor3">
					<R>0</R>
					<G>0</G>
					<B>0</B>
				</Color3>
				<double name="TextStrokeTransparency">0.5</double>
				<token name="VerticalAlignment">1</token>
				<float name="WidthScale">1</float>
				<BinaryString name="AttributesSerialize"></BinaryString>
				<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
				<bool name="DefinesCapabilities">false</bool>
				<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
				<string name="Name">ChatWindowConfiguration</string>
				<int64 name="SourceAssetId">-1</int64>
				<BinaryString name="Tags"></BinaryString>
				<UniqueId name="UniqueId">1bdada4610e5816909da199b000003b6</UniqueId>
			</Properties>
		</Item>
		<Item class="ChatInputBarConfiguration" referent="RBX81F9FC125A3F47D09C5035ED08ED5F70">
			<Properties>
				<bool name="AutocompleteEnabled">true</bool>
				<Color3 name="BackgroundColor3">
					<R>0.0980392173</R>
					<G>0.105882354</G>
					<B>0.113725491</B>
				</Color3>
				<double name="BackgroundTransparency">0.2000000000000000111</double>
				<bool name="Enabled">true</bool>
				<Font name="FontFace">
					<Family><url>rbxasset://fonts/families/BuilderSans.json</url></Family>
					<Weight>500</Weight>
					<Style>Normal</Style>
					<CachedFaceId><url>rbxasset://fonts/BuilderSans-Medium.otf</url></CachedFaceId>
				</Font>
				<token name="KeyboardKeyCode">47</token>
				<Color3 name="PlaceholderColor3">
					<R>0.698039234</R>
					<G>0.698039234</G>
					<B>0.698039234</B>
				</Color3>
				<Ref name="TargetTextChannel">null</Ref>
				<Color3 name="TextColor3">
					<R>1</R>
					<G>1</G>
					<B>1</B>
				</Color3>
				<int64 name="TextSize">18</int64>
				<Color3 name="TextStrokeColor3">
					<R>0</R>
					<G>0</G>
					<B>0</B>
				</Color3>
				<double name="TextStrokeTransparency">0.5</double>
				<BinaryString name="AttributesSerialize"></BinaryString>
				<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
				<bool name="DefinesCapabilities">false</bool>
				<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
				<string name="Name">ChatInputBarConfiguration</string>
				<int64 name="SourceAssetId">-1</int64>
				<BinaryString name="Tags"></BinaryString>
				<UniqueId name="UniqueId">1bdada4610e5816909da199b000003b7</UniqueId>
			</Properties>
		</Item>
		<Item class="BubbleChatConfiguration" referent="RBX5FFE4237DF3C4E40AC87B716E8D9FA0B">
			<Properties>
				<string name="AdorneeName">HumanoidRootPart</string>
				<Color3 name="BackgroundColor3">
					<R>0.980392158</R>
					<G>0.980392158</G>
					<B>0.980392158</B>
				</Color3>
				<double name="BackgroundTransparency">0.10000000000000000555</double>
				<float name="BubbleDuration">15</float>
				<float name="BubblesSpacing">6</float>
				<bool name="Enabled">true</bool>
				<token name="Font">47</token>
				<Font name="FontFace">
					<Family><url>rbxasset://fonts/families/BuilderSans.json</url></Family>
					<Weight>500</Weight>
					<Style>Normal</Style>
					<CachedFaceId><url>rbxasset://fonts/BuilderSans-Medium.otf</url></CachedFaceId>
				</Font>
				<Vector3 name="LocalPlayerStudsOffset">
					<X>0</X>
					<Y>0</Y>
					<Z>0</Z>
				</Vector3>
				<float name="MaxBubbles">3</float>
				<float name="MaxDistance">100</float>
				<float name="MinimizeDistance">40</float>
				<bool name="TailVisible">true</bool>
				<Color3 name="TextColor3">
					<R>0.223529413</R>
					<G>0.23137255</G>
					<B>0.239215687</B>
				</Color3>
				<int64 name="TextSize">20</int64>
				<float name="VerticalStudsOffset">0</float>
				<BinaryString name="AttributesSerialize"></BinaryString>
				<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
				<bool name="DefinesCapabilities">false</bool>
				<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
				<string name="Name">BubbleChatConfiguration</string>
				<int64 name="SourceAssetId">-1</int64>
				<BinaryString name="Tags"></BinaryString>
				<UniqueId name="UniqueId">1bdada4610e5816909da199b000003b8</UniqueId>
			</Properties>
			<Item class="UIGradient" referent="RBX27582BE1D71F4D4C88E116708215E645">
				<Properties>
					<ColorSequence name="Color">0 1 1 1 0 1 1 1 1 0 </ColorSequence>
					<bool name="Enabled">false</bool>
					<Vector2 name="Offset">
						<X>0</X>
						<Y>0</Y>
					</Vector2>
					<float name="Rotation">0</float>
					<NumberSequence name="Transparency">0 0 0 1 0 0 </NumberSequence>
					<BinaryString name="AttributesSerialize"></BinaryString>
					<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
					<bool name="DefinesCapabilities">false</bool>
					<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
					<string name="Name">UIGradient</string>
					<int64 name="SourceAssetId">-1</int64>
					<BinaryString name="Tags"></BinaryString>
					<UniqueId name="UniqueId">1bdada4610e5816909da199b000003b9</UniqueId>
				</Properties>
			</Item>
			<Item class="ImageLabel" referent="RBX64226B2240F24D7E81D206152E6814F1">
				<Properties>
					<Content name="Image"><null></null></Content>
					<Color3 name="ImageColor3">
						<R>1</R>
						<G>1</G>
						<B>1</B>
					</Color3>
					<Vector2 name="ImageRectOffset">
						<X>0</X>
						<Y>0</Y>
					</Vector2>
					<Vector2 name="ImageRectSize">
						<X>0</X>
						<Y>0</Y>
					</Vector2>
					<float name="ImageTransparency">0</float>
					<token name="ResampleMode">0</token>
					<token name="ScaleType">0</token>
					<Rect2D name="SliceCenter">
						<min>
							<X>0</X>
							<Y>0</Y>
						</min>
						<max>
							<X>0</X>
							<Y>0</Y>
						</max>
					</Rect2D>
					<float name="SliceScale">1</float>
					<UDim2 name="TileSize">
						<XS>1</XS>
						<XO>0</XO>
						<YS>1</YS>
						<YO>0</YO>
					</UDim2>
					<bool name="Active">false</bool>
					<Vector2 name="AnchorPoint">
						<X>0</X>
						<Y>0</Y>
					</Vector2>
					<token name="AutomaticSize">0</token>
					<Color3 name="BackgroundColor3">
						<R>1</R>
						<G>1</G>
						<B>1</B>
					</Color3>
					<float name="BackgroundTransparency">0</float>
					<Color3 name="BorderColor3">
						<R>0.105882362</R>
						<G>0.164705887</G>
						<B>0.207843155</B>
					</Color3>
					<token name="BorderMode">0</token>
					<int name="BorderSizePixel">1</int>
					<bool name="ClipsDescendants">false</bool>
					<bool name="Draggable">false</bool>
					<token name="InputSink">0</token>
					<bool name="Interactable">true</bool>
					<int name="LayoutOrder">0</int>
					<Ref name="NextSelectionDown">null</Ref>
					<Ref name="NextSelectionLeft">null</Ref>
					<Ref name="NextSelectionRight">null</Ref>
					<Ref name="NextSelectionUp">null</Ref>
					<UDim2 name="Position">
						<XS>0</XS>
						<XO>0</XO>
						<YS>0</YS>
						<YO>0</YO>
					</UDim2>
					<float name="Rotation">0</float>
					<bool name="Selectable">false</bool>
					<Ref name="SelectionImageObject">null</Ref>
					<int name="SelectionOrder">0</int>
					<UDim2 name="Size">
						<XS>0</XS>
						<XO>100</XO>
						<YS>0</YS>
						<YO>100</YO>
					</UDim2>
					<token name="SizeConstraint">0</token>
					<bool name="Visible">true</bool>
					<int name="ZIndex">1</int>
					<bool name="AutoLocalize">true</bool>
					<Ref name="RootLocalizationTable">null</Ref>
					<token name="SelectionBehaviorDown">0</token>
					<token name="SelectionBehaviorLeft">0</token>
					<token name="SelectionBehaviorRight">0</token>
					<token name="SelectionBehaviorUp">0</token>
					<bool name="SelectionGroup">false</bool>
					<BinaryString name="AttributesSerialize"></BinaryString>
					<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
					<bool name="DefinesCapabilities">false</bool>
					<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
					<string name="Name">ImageLabel</string>
					<int64 name="SourceAssetId">-1</int64>
					<BinaryString name="Tags"></BinaryString>
					<UniqueId name="UniqueId">1bdada4610e5816909da199b000003ba</UniqueId>
				</Properties>
			</Item>
			<Item class="UICorner" referent="RBXB1067E002C2246B5B3E5B004B0495852">
				<Properties>
					<UDim name="CornerRadius">
						<S>0</S>
						<O>12</O>
					</UDim>
					<BinaryString name="AttributesSerialize"></BinaryString>
					<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
					<bool name="DefinesCapabilities">false</bool>
					<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
					<string name="Name">UICorner</string>
					<int64 name="SourceAssetId">-1</int64>
					<BinaryString name="Tags"></BinaryString>
					<UniqueId name="UniqueId">1bdada4610e5816909da199b000003bb</UniqueId>
				</Properties>
			</Item>
			<Item class="UIPadding" referent="RBX155448895FB24C04B1A5A6AF76054039">
				<Properties>
					<UDim name="PaddingBottom">
						<S>0</S>
						<O>8</O>
					</UDim>
					<UDim name="PaddingLeft">
						<S>0</S>
						<O>8</O>
					</UDim>
					<UDim name="PaddingRight">
						<S>0</S>
						<O>8</O>
					</UDim>
					<UDim name="PaddingTop">
						<S>0</S>
						<O>8</O>
					</UDim>
					<BinaryString name="AttributesSerialize"></BinaryString>
					<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
					<bool name="DefinesCapabilities">false</bool>
					<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
					<string name="Name">UIPadding</string>
					<int64 name="SourceAssetId">-1</int64>
					<BinaryString name="Tags"></BinaryString>
					<UniqueId name="UniqueId">1bdada4610e5816909da199b000003bc</UniqueId>
				</Properties>
			</Item>
		</Item>
		<Item class="ChannelTabsConfiguration" referent="RBX19A2277E2A8D4829A22D7EF198764CC7">
			<Properties>
				<Color3 name="BackgroundColor3">
					<R>0.0980392173</R>
					<G>0.105882354</G>
					<B>0.113725491</B>
				</Color3>
				<double name="BackgroundTransparency">0</double>
				<bool name="Enabled">false</bool>
				<Font name="FontFace">
					<Family><url>rbxasset://fonts/families/BuilderSans.json</url></Family>
					<Weight>700</Weight>
					<Style>Normal</Style>
					<CachedFaceId><url>rbxasset://fonts/BuilderSans-Bold.otf</url></CachedFaceId>
				</Font>
				<Color3 name="HoverBackgroundColor3">
					<R>0.490196079</R>
					<G>0.490196079</G>
					<B>0.490196079</B>
				</Color3>
				<Color3 name="SelectedTabTextColor3">
					<R>1</R>
					<G>1</G>
					<B>1</B>
				</Color3>
				<Color3 name="TextColor3">
					<R>0.686274529</R>
					<G>0.686274529</G>
					<B>0.686274529</B>
				</Color3>
				<int64 name="TextSize">18</int64>
				<Color3 name="TextStrokeColor3">
					<R>0</R>
					<G>0</G>
					<B>0</B>
				</Color3>
				<double name="TextStrokeTransparency">1</double>
				<BinaryString name="AttributesSerialize"></BinaryString>
				<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
				<bool name="DefinesCapabilities">false</bool>
				<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
				<string name="Name">ChannelTabsConfiguration</string>
				<int64 name="SourceAssetId">-1</int64>
				<BinaryString name="Tags"></BinaryString>
				<UniqueId name="UniqueId">1bdada4610e5816909da199b000003bd</UniqueId>
			</Properties>
		</Item>
	</Item>
	<Item class="PermissionsService" referent="RBX0951D525EE494E0B9BDC9E8CAF3E4713">
		<Properties>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">PermissionsService</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b00000353</UniqueId>
		</Properties>
	</Item>
	<Item class="PlayerEmulatorService" referent="RBX62053A47E8EB44E482DDB861905C1591">
		<Properties>
			<bool name="CustomPoliciesEnabled">false</bool>
			<string name="EmulatedCountryCode"></string>
			<string name="EmulatedGameLocale"></string>
			<bool name="PlayerEmulationEnabled">false</bool>
			<bool name="PseudolocalizationEnabled">false</bool>
			<BinaryString name="SerializedEmulatedPolicyInfo"></BinaryString>
			<int name="TextElongationFactor">0</int>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">PlayerEmulatorService</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b00000354</UniqueId>
		</Properties>
	</Item>
	<Item class="StudioData" referent="RBXD85856E3E87443CA9838F5A849EDBA07">
		<Properties>
			<bool name="EnableScriptCollabByDefaultOnLoad">false</bool>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">StudioData</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b00000358</UniqueId>
		</Properties>
	</Item>
	<Item class="StarterPlayer" referent="RBXEC3A0C927EB44D5798C059A7CE4D27CA">
		<Properties>
			<bool name="AllowCustomAnimations">true</bool>
			<bool name="AutoJumpEnabled">true</bool>
			<token name="AvatarJointUpgrade_SerializedRollout">2</token>
			<float name="CameraMaxZoomDistance">128</float>
			<float name="CameraMinZoomDistance">0.5</float>
			<token name="CameraMode">0</token>
			<bool name="CharacterBreakJointsOnDeath">false</bool>
			<float name="CharacterJumpHeight">7.19999981</float>
			<float name="CharacterJumpPower">50</float>
			<float name="CharacterMaxSlopeAngle">89</float>
			<bool name="CharacterUseJumpPower">false</bool>
			<float name="CharacterWalkSpeed">16</float>
			<bool name="ClassicDeath">true</bool>
			<bool name="CreateDefaultPlayerModule">true</bool>
			<token name="DevCameraOcclusionMode">0</token>
			<token name="DevComputerCameraMovementMode">0</token>
			<token name="DevComputerMovementMode">0</token>
			<token name="DevTouchCameraMovementMode">0</token>
			<token name="DevTouchMovementMode">0</token>
			<token name="EnableDynamicHeads">0</token>
			<bool name="EnableMouseLockOption">true</bool>
			<int64 name="GameSettingsAssetIDFace">0</int64>
			<int64 name="GameSettingsAssetIDHead">0</int64>
			<int64 name="GameSettingsAssetIDLeftArm">0</int64>
			<int64 name="GameSettingsAssetIDLeftLeg">0</int64>
			<int64 name="GameSettingsAssetIDPants">0</int64>
			<int64 name="GameSettingsAssetIDRightArm">0</int64>
			<int64 name="GameSettingsAssetIDRightLeg">0</int64>
			<int64 name="GameSettingsAssetIDShirt">0</int64>
			<int64 name="GameSettingsAssetIDTeeShirt">0</int64>
			<int64 name="GameSettingsAssetIDTorso">0</int64>
			<token name="GameSettingsAvatar">1</token>
			<token name="GameSettingsR15Collision">0</token>
			<NumberRange name="GameSettingsScaleRangeBodyType">0 1 </NumberRange>
			<NumberRange name="GameSettingsScaleRangeHead">0.95 1 </NumberRange>
			<NumberRange name="GameSettingsScaleRangeHeight">0.9 1.05 </NumberRange>
			<NumberRange name="GameSettingsScaleRangeProportion">0 1 </NumberRange>
			<NumberRange name="GameSettingsScaleRangeWidth">0.7 1 </NumberRange>
			<float name="HealthDisplayDistance">100</float>
			<bool name="LoadCharacterAppearance">true</bool>
			<token name="LoadCharacterLayeredClothing">0</token>
			<token name="LuaCharacterController">0</token>
			<float name="NameDisplayDistance">100</float>
			<bool name="UserEmotesEnabled">true</bool>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">StarterPlayer</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b0000035a</UniqueId>
		</Properties>
		<Item class="StarterPlayerScripts" referent="RBXAA488F007A804BECABD70C85D4D4B679">
			<Properties>
				<BinaryString name="AttributesSerialize"></BinaryString>
				<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
				<bool name="DefinesCapabilities">false</bool>
				<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
				<string name="Name">StarterPlayerScripts</string>
				<int64 name="SourceAssetId">-1</int64>
				<BinaryString name="Tags"></BinaryString>
				<UniqueId name="UniqueId">1bdada4610e5816909da199b000003ae</UniqueId>
			</Properties>
		</Item>
		<Item class="StarterCharacterScripts" referent="RBX12FA2BAA05384D3FB724902501754E32">
			<Properties>
				<BinaryString name="AttributesSerialize"></BinaryString>
				<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
				<bool name="DefinesCapabilities">false</bool>
				<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
				<string name="Name">StarterCharacterScripts</string>
				<int64 name="SourceAssetId">-1</int64>
				<BinaryString name="Tags"></BinaryString>
				<UniqueId name="UniqueId">1bdada4610e5816909da199b000003af</UniqueId>
			</Properties>
		</Item>
	</Item>
	<Item class="StarterPack" referent="RBX146B2AED03ED433EB358A111B51332E0">
		<Properties>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">StarterPack</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b0000035b</UniqueId>
		</Properties>
	</Item>
	<Item class="StarterGui" referent="RBXCB7077ABFCFC4004A404AD4C90F8FFAE">
		<Properties>
			<bool name="ResetPlayerGuiOnSpawn">true</bool>
			<token name="RtlTextSupport">0</token>
			<token name="ScreenOrientation">4</token>
			<bool name="ShowDevelopmentGui">true</bool>
			<Ref name="StudioDefaultStyleSheet">null</Ref>
			<Ref name="StudioInsertWidgetLayerCollectorAutoLinkStyleSheet">null</Ref>
			<token name="VirtualCursorMode">0</token>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">StarterGui</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b0000035c</UniqueId>
		</Properties>
	</Item>
	<Item class="LocalizationService" referent="RBX903E13AFE86C4BB8B7C28ECBD2CF2B67">
		<Properties>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">LocalizationService</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b0000035e</UniqueId>
		</Properties>
	</Item>
	<Item class="TeleportService" referent="RBX02218BC147BA48B4BFFA8A08D7AC8384">
		<Properties>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">Teleport Service</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b00000362</UniqueId>
		</Properties>
	</Item>
	<Item class="CollectionService" referent="RBX45F687B7C4874666B0C3400D20878B09">
		<Properties>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">CollectionService</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b00000364</UniqueId>
		</Properties>
	</Item>
	<Item class="PhysicsService" referent="RBX38D56D20710947F5A32A2FFA2B517D86">
		<Properties>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">PhysicsService</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b00000365</UniqueId>
		</Properties>
	</Item>
	<Item class="InsertService" referent="RBX4A772EEDFF2D4847A90AE9AEA7A4A005">
		<Properties>
			<bool name="AllowClientInsertModels">false</bool>
			<bool name="AllowInsertFreeModels">false</bool>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">InsertService</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b00000368</UniqueId>
		</Properties>
		<Item class="StringValue" referent="RBXF33C023DE5B44251AD5287AD6DC9F17E">
			<Properties>
				<string name="Value">{14656B85-40CA-4127-8120-C9EEA4F92501}</string>
				<BinaryString name="AttributesSerialize"></BinaryString>
				<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
				<bool name="DefinesCapabilities">false</bool>
				<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
				<string name="Name">InsertionHash</string>
				<int64 name="SourceAssetId">-1</int64>
				<BinaryString name="Tags"></BinaryString>
				<UniqueId name="UniqueId">1bdada4610e5816909da199b000003b0</UniqueId>
			</Properties>
		</Item>
	</Item>
	<Item class="GamePassService" referent="RBXD71E98D2871547BDA4EFCFF2ADE47739">
		<Properties>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">GamePassService</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b00000369</UniqueId>
		</Properties>
	</Item>
	<Item class="Debris" referent="RBX917B3E4E09164A9586CA50E89D16C312">
		<Properties>
			<int name="MaxItems">1000</int>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">Debris</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b0000036a</UniqueId>
		</Properties>
	</Item>
	<Item class="CookiesService" referent="RBXEF8992ABF7A54DFABAC7F59B2BDF711C">
		<Properties>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">CookiesService</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b0000036b</UniqueId>
		</Properties>
	</Item>
	<Item class="Selection" referent="RBX2E540F73C12F47258366FD6DF83D6340">
		<Properties>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">Selection</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b0000036c</UniqueId>
		</Properties>
	</Item>
	<Item class="VRService" referent="RBXF47D35439CA94851AB6DB9A09FC6A8A1">
		<Properties>
			<token name="AutomaticScaling">0</token>
			<bool name="AvatarGestures">false</bool>
			<token name="ControllerModels">1</token>
			<bool name="FadeOutViewOnCollision">true</bool>
			<token name="LaserPointer">1</token>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">VRService</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b00000370</UniqueId>
		</Properties>
	</Item>
	<Item class="ContextActionService" referent="RBXBD26B1554559430A8158D8014D19FB3E">
		<Properties>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">ContextActionService</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b00000371</UniqueId>
		</Properties>
	</Item>
	<Item class="ScriptService" referent="RBX8D42F1F449A24123A925BDAAE657C24E">
		<Properties>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">Instance</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b00000372</UniqueId>
		</Properties>
	</Item>
	<Item class="AssetService" referent="RBXD1D5BD18338C47FC845D35F52C3B1CAA">
		<Properties>
			<bool name="AllowInsertFreeAssets">false</bool>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">AssetService</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b00000373</UniqueId>
		</Properties>
	</Item>
	<Item class="TouchInputService" referent="RBX198D0B965D394414B4425F067934285C">
		<Properties>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">TouchInputService</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b00000375</UniqueId>
		</Properties>
	</Item>
	<Item class="AvatarSettings" referent="RBX2EC5664E08E8469EA35B4A2E3BAAD02C">
		<Properties>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">AvatarSettings</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b0000037b</UniqueId>
		</Properties>
	</Item>
	<Item class="LuaWebService" referent="RBX95D6655100E94903B809B005A04960BF">
		<Properties>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">LuaWebService</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b00000383</UniqueId>
		</Properties>
	</Item>
	<Item class="ProcessInstancePhysicsService" referent="RBX57478BBCF68C4AC994C8C6F4672F35DA">
		<Properties>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">ProcessInstancePhysicsService</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b00000384</UniqueId>
		</Properties>
	</Item>
	<Item class="ReplicatedStorage" referent="RBX7784D63E851D4404B624C530D384738F">
		<Properties>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">ReplicatedStorage</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b00000385</UniqueId>
		</Properties>
	</Item>
	<Item class="ServerScriptService" referent="RBXB027EF6D7CC049E78E10D06058BDBE85">
		<Properties>
			<bool name="LoadStringEnabled">false</bool>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">ServerScriptService</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b00000386</UniqueId>
		</Properties>
	</Item>
	<Item class="ServerStorage" referent="RBX25AF993BACEF4704853B0E7EF163DCEA">
		<Properties>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">ServerStorage</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b00000387</UniqueId>
		</Properties>
	</Item>
	<Item class="ServiceVisibilityService" referent="RBXC354316F606F4E198B8F4032BF9B3C39">
		<Properties>
			<BinaryString name="HiddenServices">AAAAAA==</BinaryString>
			<BinaryString name="VisibleServices">AAAAAA==</BinaryString>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">ServiceVisibilityService</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b0000038c</UniqueId>
		</Properties>
	</Item>
	<Item class="HttpService" referent="RBXFC238FB5DA4A49A38AB9AEB25E600D96">
		<Properties>
			<bool name="HttpEnabled">false</bool>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">HttpService</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b00000396</UniqueId>
		</Properties>
	</Item>
	<Item class="DataStoreService" referent="RBX31D4E715AAF2459988D79495DAA8F249">
		<Properties>
			<bool name="AutomaticRetry">true</bool>
			<bool name="LegacyNamingScheme">false</bool>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">DataStoreService</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b0000039e</UniqueId>
		</Properties>
	</Item>
	<Item class="Lighting" referent="RBX15EFC5B448AE473DAB8C1E71B07E7BF9">
		<Properties>
			<Color3 name="Ambient">
				<R>0.274509817</R>
				<G>0.274509817</G>
				<B>0.274509817</B>
			</Color3>
			<float name="Brightness">3</float>
			<Color3 name="ColorShift_Bottom">
				<R>0</R>
				<G>0</G>
				<B>0</B>
			</Color3>
			<Color3 name="ColorShift_Top">
				<R>0</R>
				<G>0</G>
				<B>0</B>
			</Color3>
			<float name="EnvironmentDiffuseScale">1</float>
			<float name="EnvironmentSpecularScale">1</float>
			<float name="ExposureCompensation">0</float>
			<token name="ExtendLightRangeTo120">0</token>
			<Color3 name="FogColor">
				<R>0.752941251</R>
				<G>0.752941251</G>
				<B>0.752941251</B>
			</Color3>
			<float name="FogEnd">100000</float>
			<float name="FogStart">0</float>
			<float name="GeographicLatitude">0</float>
			<bool name="GlobalShadows">true</bool>
			<token name="LightingStyle">1</token>
			<Color3 name="OutdoorAmbient">
				<R>0.274509817</R>
				<G>0.274509817</G>
				<B>0.274509817</B>
			</Color3>
			<bool name="Outlines">false</bool>
			<bool name="PrioritizeLightingQuality">true</bool>
			<float name="ShadowSoftness">0.200000003</float>
			<token name="Technology">3</token>
			<string name="TimeOfDay">14:30:00</string>
			<BinaryString name="AttributesSerialize"><![CDATA[AgAAACYAAABSQlhfTGlnaHRpbmdUZWNobm9sb2d5VW5pZmllZE1pZ3JhdGlvbgMBIAAAAFJC
WF9PcmlnaW5hbFRlY2hub2xvZ3lPbkZpbGVMb2FkBAMAAAA=]]></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">Lighting</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b0000039f</UniqueId>
		</Properties>
		<Item class="Sky" referent="RBX9685D7DF05834CE5A0F066F7035676DE">
			<Properties>
				<bool name="CelestialBodiesShown">true</bool>
				<float name="MoonAngularSize">11</float>
				<Content name="MoonTextureId"><url>rbxassetid://6444320592</url></Content>
				<Content name="SkyboxBk"><url>rbxassetid://6444884337</url></Content>
				<Content name="SkyboxDn"><url>rbxassetid://6444884785</url></Content>
				<Content name="SkyboxFt"><url>rbxassetid://6444884337</url></Content>
				<Content name="SkyboxLf"><url>rbxassetid://6444884337</url></Content>
				<Vector3 name="SkyboxOrientation">
					<X>0</X>
					<Y>0</Y>
					<Z>0</Z>
				</Vector3>
				<Content name="SkyboxRt"><url>rbxassetid://6444884337</url></Content>
				<Content name="SkyboxUp"><url>rbxassetid://6412503613</url></Content>
				<int name="StarCount">3000</int>
				<float name="SunAngularSize">11</float>
				<Content name="SunTextureId"><url>rbxassetid://6196665106</url></Content>
				<BinaryString name="AttributesSerialize"></BinaryString>
				<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
				<bool name="DefinesCapabilities">false</bool>
				<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
				<string name="Name">Sky</string>
				<int64 name="SourceAssetId">332039975</int64>
				<BinaryString name="Tags"></BinaryString>
				<UniqueId name="UniqueId">1bdada4610e5816909da199b000003b1</UniqueId>
			</Properties>
		</Item>
		<Item class="SunRaysEffect" referent="RBX7C5DCB4504B14064B369393D37BA77BE">
			<Properties>
				<float name="Intensity">0.00999999978</float>
				<float name="Spread">0.100000001</float>
				<bool name="Enabled">true</bool>
				<BinaryString name="AttributesSerialize"></BinaryString>
				<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
				<bool name="DefinesCapabilities">false</bool>
				<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
				<string name="Name">SunRays</string>
				<int64 name="SourceAssetId">-1</int64>
				<BinaryString name="Tags"></BinaryString>
				<UniqueId name="UniqueId">1bdada4610e5816909da199b000003b2</UniqueId>
			</Properties>
		</Item>
		<Item class="Atmosphere" referent="RBXCF02155A23BA4FC2B1F52184240B7532">
			<Properties>
				<Color3 name="Color">
					<R>0.78039217</R>
					<G>0.78039217</G>
					<B>0.78039217</B>
				</Color3>
				<Color3 name="Decay">
					<R>0.41568628</R>
					<G>0.43921569</G>
					<B>0.490196079</B>
				</Color3>
				<float name="Density">0.300000012</float>
				<float name="Glare">0</float>
				<float name="Haze">0</float>
				<float name="Offset">0.25</float>
				<BinaryString name="AttributesSerialize"></BinaryString>
				<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
				<bool name="DefinesCapabilities">false</bool>
				<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
				<string name="Name">Atmosphere</string>
				<int64 name="SourceAssetId">-1</int64>
				<BinaryString name="Tags"></BinaryString>
				<UniqueId name="UniqueId">1bdada4610e5816909da199b000003b3</UniqueId>
			</Properties>
		</Item>
		<Item class="BloomEffect" referent="RBXDFD955CB358D43F68B3BA7704E9A716E">
			<Properties>
				<float name="Intensity">1</float>
				<float name="Size">24</float>
				<float name="Threshold">2</float>
				<bool name="Enabled">true</bool>
				<BinaryString name="AttributesSerialize"></BinaryString>
				<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
				<bool name="DefinesCapabilities">false</bool>
				<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
				<string name="Name">Bloom</string>
				<int64 name="SourceAssetId">-1</int64>
				<BinaryString name="Tags"></BinaryString>
				<UniqueId name="UniqueId">1bdada4610e5816909da199b000003b4</UniqueId>
			</Properties>
		</Item>
		<Item class="DepthOfFieldEffect" referent="RBXEFB4EBD9A76642C4B4D5FE8DA984831F">
			<Properties>
				<float name="FarIntensity">0.100000001</float>
				<float name="FocusDistance">0.0500000007</float>
				<float name="InFocusRadius">30</float>
				<float name="NearIntensity">0.75</float>
				<bool name="Enabled">false</bool>
				<BinaryString name="AttributesSerialize"></BinaryString>
				<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
				<bool name="DefinesCapabilities">false</bool>
				<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
				<string name="Name">DepthOfField</string>
				<int64 name="SourceAssetId">-1</int64>
				<BinaryString name="Tags"></BinaryString>
				<UniqueId name="UniqueId">1bdada4610e5816909da199b000003b5</UniqueId>
			</Properties>
		</Item>
	</Item>
	<Item class="LodDataService" referent="RBXF569724AA2DA4FF493F5932565C089FD">
		<Properties>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">Instance</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b000003a0</UniqueId>
		</Properties>
	</Item>
	<Item class="ProximityPromptService" referent="RBXE897A59A486944269C7177D82906CC22">
		<Properties>
			<bool name="Enabled">true</bool>
			<int name="MaxIndicatorsVisible">16</int>
			<int name="MaxPromptsVisible">16</int>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">ProximityPromptService</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b000003a1</UniqueId>
		</Properties>
	</Item>
	<Item class="Teams" referent="RBX74B773BE39CF45CDB4AC31674E47F5BE">
		<Properties>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">Teams</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b000003a2</UniqueId>
		</Properties>
	</Item>
	<Item class="TestService" referent="RBX6BD6B41836C04F4D955589D5B3997CE1">
		<Properties>
			<bool name="AutoRuns">true</bool>
			<string name="Description"></string>
			<bool name="ExecuteWithStudioRun">false</bool>
			<bool name="IsPhysicsEnvironmentalThrottled">true</bool>
			<bool name="IsSleepAllowed">true</bool>
			<int name="NumberOfPlayers">0</int>
			<double name="SimulateSecondsLag">0</double>
			<bool name="ThrottlePhysicsToRealtime">true</bool>
			<double name="Timeout">10</double>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">TestService</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b000003a3</UniqueId>
		</Properties>
		<Item class="ModuleScript" referent="RBX3E32982C06DC47D38270FDCA6E12BB9D">
			<Properties>
				<Content name="LinkedSource"><null></null></Content>
				<ProtectedString name="Source"><![CDATA[--- Configuration for the Luau Language Server
--- https://devforum.roblox.com/t/luau-language-server-for-external-editors/2185389
--- Make sure that `luau-lsp.plugin.enabled` is set to `true` in VSCode for the plugin to connect

return {
	--- The host to connect to the language server.
	host = "http://localhost",

	--- The port to connect to the language server.
	--- In VSCode, this is configured using `luau-lsp.plugin.port`
	--- Note, this port is *different* to your Rojo port
	port = 3667,

	--- Whether the plugin should automatically connect to the language server when Studio starts up
	startAutomatically = false,

	--- A list of Instances to track for changes.
	--- When any descendants of these instances change, an update event is sent to the language server
	include = {
		game:GetService("Workspace"),
		game:GetService("Players"),
		game:GetService("Lighting"),
		game:GetService("ReplicatedFirst"),
		game:GetService("ReplicatedStorage"),
		game:GetService("ServerScriptService"),
		game:GetService("ServerStorage"),
		game:GetService("StarterGui"),
		game:GetService("StarterPack"),
		game:GetService("StarterPlayer"),
		game:GetService("SoundService"),
		game:GetService("Chat"),
		game:GetService("LocalizationService"),
		game:GetService("TestService"),
	},

	--- The log level to use for the language server.
	--- Valid values are "DEBUG", "INFO", "WARN", "ERROR"
	logLevel = "INFO",
}
]]></ProtectedString>
				<string name="ScriptGuid">{DD192BE9-9134-402C-9F6E-C0636A4824FD}</string>
				<BinaryString name="AttributesSerialize"></BinaryString>
				<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
				<bool name="DefinesCapabilities">false</bool>
				<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
				<string name="Name">LuauLSP_Settings</string>
				<int64 name="SourceAssetId">-1</int64>
				<BinaryString name="Tags"></BinaryString>
				<UniqueId name="UniqueId">1bdada4610e5816909da199b000005f7</UniqueId>
			</Properties>
		</Item>
	</Item>
	<Item class="UGCAvatarService" referent="RBXF7692F12270E4E23B4EA133D6F1C3C9C">
		<Properties>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">UGCAvatarService</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b000003a4</UniqueId>
		</Properties>
	</Item>
	<Item class="VirtualInputManager" referent="RBX62D82406A934404380990ADC1D042127">
		<Properties>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">VirtualInputManager</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b000003a5</UniqueId>
		</Properties>
	</Item>
	<Item class="VoiceChatService" referent="RBX7B6607B0FEFD4524BD8A43C17BA9AAAF">
		<Properties>
			<token name="DefaultDistanceAttenuation">0</token>
			<bool name="EnableDefaultVoice">true</bool>
			<token name="UseAudioApi">2</token>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">VoiceChatService</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b000003a6</UniqueId>
		</Properties>
	</Item>
	<Item class="VideoService" referent="RBX5C33C9318E2C4EF2922881D0587DD0FB">
		<Properties>
			<BinaryString name="AttributesSerialize"></BinaryString>
			<SecurityCapabilities name="Capabilities">0</SecurityCapabilities>
			<bool name="DefinesCapabilities">false</bool>
			<UniqueId name="HistoryId">00000000000000000000000000000000</UniqueId>
			<string name="Name">VideoService</string>
			<int64 name="SourceAssetId">-1</int64>
			<BinaryString name="Tags"></BinaryString>
			<UniqueId name="UniqueId">1bdada4610e5816909da199b0000060e</UniqueId>
		</Properties>
	</Item>
	<SharedStrings>
		<SharedString md5="yuZpQdnvvUBOTYh1jqZ2cA=="></SharedString>
	</SharedStrings>
</roblox>"""

# =========================================================
# HELPERS
# =========================================================
def esc(v):
    return xml_escape(str(v))

def new_ref():
    return "RBX" + uuid.uuid4().hex.upper()

def num_list(v, n, default):
    if not isinstance(v, list):
        return default
    return [(v[i] if i < len(v) else default[i]) for i in range(n)]

def get_workspace_referent(template_text: str) -> str:
    m = re.search(r'<Item class="Workspace" referent="([^"]+)">', template_text)
    if not m:
        raise ValueError("Workspace referent not found in template")
    return m.group(1)

def find_matching_item_close(template_text: str, open_index: int) -> int:
    depth = 0
    i = open_index

    while True:
        next_open = template_text.find("<Item ", i)
        next_close = template_text.find("</Item>", i)

        if next_close == -1:
            raise ValueError("Could not find matching </Item>")

        if next_open != -1 and next_open < next_close:
            depth += 1
            i = next_open + 5
        else:
            depth -= 1
            i = next_close + len("</Item>")
            if depth == 0:
                return next_close

# =========================================================
# ENUM TOKENS
# =========================================================
def token_material(v):
    s = str(v).lower()

    if "plastic" in s:
        return "256"
    if "smoothplastic" in s:
        return "272"
    if "neon" in s:
        return "288"
    if "wood" in s:
        return "512"
    if "slate" in s:
        return "800"
    if "concrete" in s:
        return "816"
    if "corrodedmetal" in s:
        return "1040"
    if "diamondplate" in s:
        return "1056"
    if "foil" in s:
        return "1072"
    if "grass" in s:
        return "1280"
    if "ice" in s:
        return "1536"
    if "crackedlava" in s:
        return "1792"

    return "256"

def token_surface(v):
    s = str(v).lower()

    if "smooth" in s:
        return "0"
    if "studs" in s:
        return "1"
    if "inlet" in s:
        return "2"
    if "universal" in s:
        return "3"
    if "glue" in s:
        return "4"
    if "weld" in s:
        return "5"

    return "0"

# =========================================================
# BUILD INSTANCE
# =========================================================
def build_instance(data, parent_ref):
    ref = new_ref()

    size = num_list(data.get("Size", [4, 4, 4]), 3, [4, 4, 4])
    color = num_list(data.get("Color", [163, 162, 165]), 3, [163, 162, 165])
    cf = num_list(
        data.get("CFrame", [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1]),
        12,
        [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1]
    )

    cls = data.get("ClassName", "Part")
    name = data.get("Name", "Part")

    xml = []
    xml.append(f'<Item class="{cls}" referent="{ref}">')
    xml.append("<Properties>")
    xml.append(f"<string name=\"Name\">{esc(name)}</string>")
    xml.append(f"<Vector3 name=\"Size\"><X>{size[0]}</X><Y>{size[1]}</Y><Z>{size[2]}</Z></Vector3>")

    xml.append("<CoordinateFrame name=\"CFrame\">")
    xml.append(f"<X>{cf[0]}</X><Y>{cf[1]}</Y><Z>{cf[2]}</Z>")
    xml.append(f"<R00>{cf[3]}</R00><R01>{cf[4]}</R01><R02>{cf[5]}</R02>")
    xml.append(f"<R10>{cf[6]}</R10><R11>{cf[7]}</R11><R12>{cf[8]}</R12>")
    xml.append(f"<R20>{cf[9]}</R20><R21>{cf[10]}</R21><R22>{cf[11]}</R22>")
    xml.append("</CoordinateFrame>")

    # Match your real template's color style
    xml.append(
        f'<Color3 name="Color3"><R>{color[0]/255}</R><G>{color[1]/255}</G><B>{color[2]/255}</B></Color3>'
    )
    xml.append('<int name="BrickColor">194</int>')

    xml.append(f'<bool name="Anchored">{"true" if data.get("Anchored", True) else "false"}</bool>')
    xml.append(f'<bool name="CanCollide">{"true" if data.get("CanCollide", True) else "false"}</bool>')
    xml.append(f'<bool name="CanTouch">{"true" if data.get("CanTouch", True) else "false"}</bool>')
    xml.append(f'<bool name="CanQuery">{"true" if data.get("CanQuery", True) else "false"}</bool>')
    xml.append(f'<float name="Transparency">{data.get("Transparency", 0)}</float>')
    xml.append(f'<float name="Reflectance">{data.get("Reflectance", 0)}</float>')
    xml.append(f'<bool name="CastShadow">{"true" if data.get("CastShadow", True) else "false"}</bool>')
    xml.append('<bool name="Locked">false</bool>')

    xml.append(f'<token name="TopSurface">{token_surface(data.get("TopSurface"))}</token>')
    xml.append(f'<token name="BottomSurface">{token_surface(data.get("BottomSurface"))}</token>')
    xml.append('<token name="FrontSurface">0</token>')
    xml.append('<token name="BackSurface">0</token>')
    xml.append('<token name="LeftSurface">0</token>')
    xml.append('<token name="RightSurface">0</token>')

    xml.append(f'<token name="Material">{token_material(data.get("Material"))}</token>')
    xml.append('<bool name="Archivable">true</bool>')
    xml.append(f'<Ref name="Parent">{parent_ref}</Ref>')

    if cls == "SpawnLocation":
        xml.append('<float name="Duration">5</float>')
        xml.append('<bool name="Neutral">true</bool>')

    xml.append("</Properties>")
    xml.append("</Item>")
    return "\n".join(xml)

# =========================================================
# BUILD RBXLX
# =========================================================
def build_rbxlx(instances):
    template = TEMPLATE
    if "PASTE_YOUR_REAL_RBXLX_TEMPLATE_HERE" in template:
        raise ValueError("Paste your real template into the TEMPLATE string first.")

    workspace_ref = get_workspace_referent(template)

    workspace_open = f'<Item class="Workspace" referent="{workspace_ref}">'
    ws_start = template.find(workspace_open)
    if ws_start == -1:
        raise ValueError("Workspace block not found in template")

    props_end = template.find("</Properties>", ws_start)
    if props_end == -1:
        raise ValueError("Workspace </Properties> not found")

    ws_close = find_matching_item_close(template, ws_start)
    if ws_close == -1:
        raise ValueError("Workspace closing </Item> not found")

    content = ""
    for inst in instances:
        content += build_instance(inst, workspace_ref) + "\n"

    # Replace only the children inside Workspace, preserve the rest of the real template
    return template[:props_end + len("</Properties>")] + "\n" + content + template[ws_close:]

# =========================================================
# ROUTE
# =========================================================
@app.route("/publish", methods=["POST"])
def publish():
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        api_key = data.get("apiKey")
        universe_id = data.get("universeId")
        place_id = data.get("placeId")
        instances = data.get("instances", [])

        if not api_key or not universe_id or not place_id:
            return jsonify({"error": "Missing required fields"}), 400

        xml_data = build_rbxlx(instances)

        url = f"https://apis.roblox.com/universes/v1/{universe_id}/places/{place_id}/versions"
        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/xml"
        }

        res = requests.post(
            url,
            headers=headers,
            params={"versionType": "Published"},
            data=xml_data,
            timeout=60
        )

        return jsonify({
            "status": res.status_code,
            "response": res.text
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =========================================================
# RUN
# =========================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
