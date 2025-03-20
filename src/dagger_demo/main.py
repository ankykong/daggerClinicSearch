import dagger
from dagger import dag, function, object_type, enum_type, DefaultPath, LlmWorkspace
from typing import Annotated


@enum_type
class VisitReason(dagger.Enum):
    HOSPITAL = "hospital"
    DOCTOR = "doctor"
    CHIROPRACTOR = "chiropractor"
    DENTIST = "dentist"
    DENTAL_CLINIC = "dental_clinic"
    MEDICAL_LAB = "medical_lab"


@object_type
class DaggerDemo:
    patient_data_file: Annotated[dagger.File, DefaultPath("mock_patient_data.json")]

    # @function
    # async def debug_place_search(
    #         self,
    #         # visit_reasons: list[VisitReason],
    #         loc_arg: str,
    #         # rad_arg: str
    # ) -> dagger.Container:
    #     dir = dag.current_module().source().directory("api_calls")
    #     ctr = await (
    #         dag.container()
    #         .from_("python:3.11-alpine")
    #         .terminal(insecure_root_capabilities=True)
    #         # .with_exec(["pip", "install", "requests", "python-dotenv"])
    #         # .with_mounted_directory("/api_calls", dir)
    #         # .with_workdir("/api_calls")

    #     )
    #     return ctr
    #     # full_response = await ctr.with_exec(["python", "geocoding_api_call.py", loc_arg]).stdout()

    #     # coordinates = await ctr.with_exec(["python", "coord_parser.py"], stdin=full_response).stdout()
    #     # return coordinates

    @function
    def llm_parser(self) -> str:
        llm = dag.llm(
            model="gemini-2.0-flash")
        json_output_str = llm.with_file(self.patient_data_file).with_prompt("""
            First respond with the contents of the file.
            Here is the VisitReason Enum:
            class VisitReason(dagger.Enum):
                HOSPITAL = "hospital"
                DOCTOR = "doctor"
                CHIROPRACTOR = "chiropractor"
                DENTIST = "dentist"
                DENTAL_CLINIC = "dental_clinic"
                MEDICAL_LAB = "medical_lab"
            Extract all the following information from 'patient_data_file'. Do not give code, just do the task! Extract the visit reason so that it complies with the VisitReason Enum. Extract the radiius in meters. Extract location. Put it all in a JSON File named 'place_data.json'
        """).last_reply()
        return json_output_str

    @function
    async def place_search(
            self,
            visit_reason: VisitReason,
            loc_arg: str,
            rad_arg: str,
    ) -> str:
        dir = dag.current_module().source().directory("api_calls")
        ctr = await (
            dag.container()
            .from_("python:3.11-alpine")
            .with_exec(["pip", "install", "requests", "python-dotenv"])
            .with_mounted_directory("/api_calls", dir)
            .with_workdir("/api_calls")
        )
        full_response = await ctr.with_exec(["python", "geocoding_api_call.py", loc_arg]).file("geocoding_result.json").contents()

        # Get the file contents as a string
        coordinates_str = await ctr.with_exec(["python", "coord_parser.py"], stdin=full_response).file("parsed_coordinates.json").contents()

        # Parse the string to a JSON object
        import json
        coordinates_obj = json.loads(coordinates_str)

        # Extract latitude and longitude
        latitude = coordinates_obj["latitude"]
        longitude = coordinates_obj["longitude"]

        nearby_places = await ctr.with_exec(["python", "nearby_api_call.py", latitude, longitude, rad_arg, visit_reason]).file("nearby_places_result.json").contents()
        return nearby_places

    @function
    def container_echo(self, string_arg: str) -> str:
        """Returns a container that echoes whatever string argument is provided"""
        return dag.container().from_("alpine:latest").with_exec(["echo", string_arg]).stdout()

    @function
    async def grep_dir(self, directory_arg: dagger.Directory, pattern: str) -> str:
        """Returns lines that match a pattern in the files of the provided Directory"""
        return await (
            dag.container()
            .from_("alpine:latest")
            .with_mounted_directory("/mnt", directory_arg)
            .with_workdir("/mnt")
            .with_exec(["grep", "-R", pattern, "."])
            .stdout()
        )
