import argparse
from typing import List

from .proxies import GenericProxyConfig, WebshareProxyConfig
from .formatters import FormatterLoader

from ._api import YouTubeTranscriptApi, FetchedTranscript, TranscriptList


class YouTubeTranscriptCli:
    def __init__(self, args: List[str]):
        self._args = args

    def run(self) -> str:
        parsed_args = self._parse_args()

        if parsed_args.exclude_manually_created and parsed_args.exclude_generated:
            return ""

        proxy_config = None
        if parsed_args.http_proxy != "" or parsed_args.https_proxy != "":
            proxy_config = GenericProxyConfig(
                http_url=parsed_args.http_proxy,
                https_url=parsed_args.https_proxy,
            )

        if (
            parsed_args.webshare_proxy_username is not None
            or parsed_args.webshare_proxy_password is not None
        ):
            proxy_config = WebshareProxyConfig(
                proxy_username=parsed_args.webshare_proxy_username,
                proxy_password=parsed_args.webshare_proxy_password,
            )

        cookie_path = parsed_args.cookies
        scrapeops_api_key = parsed_args.scrapeops_api_key

        transcripts = []
        exceptions = []

        ytt_api = YouTubeTranscriptApi(
            proxy_config=proxy_config,
            cookie_path=cookie_path,
            scrapeops_api_key=scrapeops_api_key,
        )

        for video_id in parsed_args.video_ids:
            try:
                transcript_list = ytt_api.list(video_id)
                if parsed_args.list_transcripts:
                    transcripts.append(transcript_list)
                else:
                    transcripts.append(
                        self._fetch_transcript(
                            parsed_args,
                            transcript_list,
                        )
                    )
            except Exception as exception:
                exceptions.append(exception)

        print_sections = [str(exception) for exception in exceptions]
        if transcripts:
            if parsed_args.list_transcripts:
                print_sections.extend(
                    str(transcript_list) for transcript_list in transcripts
                )
            else:
                print_sections.append(
                    FormatterLoader()
                    .load(parsed_args.format)
                    .format_transcripts(transcripts)
                )

        return "\n\n".join(print_sections)

    def _fetch_transcript(
        self,
        parsed_args,
        transcript_list: TranscriptList,
    ) -> FetchedTranscript:
        if parsed_args.exclude_manually_created:
            transcript = transcript_list.find_generated_transcript(
                parsed_args.languages
            )
        elif parsed_args.exclude_generated:
            transcript = transcript_list.find_manually_created_transcript(
                parsed_args.languages
            )
        else:
            transcript = transcript_list.find_transcript(parsed_args.languages)

        if parsed_args.translate:
            transcript = transcript.translate(parsed_args.translate)

        return transcript.fetch()

    def _parse_args(self):
        parser = argparse.ArgumentParser(
            description='This is an alternative way to use the YouTube Transcript API. '
            'When you use this from the command line, it will print the transcript out to the command line. '
            'If you pipe a file into the command, it will treat each line as a video id',
        )

        parser.add_argument(
            'video_ids',
            nargs='*',
            help='The ids of the YouTube videos for which the subtitle should be fetched.',
        )

        parser.add_argument(
            '--format',
            default='plain',
            const='plain',
            nargs='?',
            choices=self._build_available_formats(),
            help='Output format for the transcript.',
        )

        parser.add_argument(
            '--languages',
            nargs='*',
            default=['en'],
            help='A list of language codes in a descending priority. For example, if this is set to "de en", '
            'it will first try to fetch the german transcript (de) and then fetch the english transcript (en) '
            'if it fails to do so.',
        )

        parser.add_argument(
            '--http-proxy',
            default='',
            help='HTTP proxy used when fetching transcripts',
        )

        parser.add_argument(
            '--https-proxy',
            default='',
            help='HTTPS proxy used when fetching transcripts',
        )

        parser.add_argument(
            '--webshare-proxy-username',
            help='Webshare proxy username',
        )

        parser.add_argument(
            '--webshare-proxy-password',
            help='Webshare proxy password',
        )

        parser.add_argument(
            '--cookies',
            help='Path to cookies file. Cookies should be in Mozilla/Netscape format.',
        )

        parser.add_argument(
            '--scrapeops-api-key',
            help='ScrapeOps API key for making requests through their proxy service.',
        )

        parser.add_argument(
            '--list-transcripts',
            action='store_true',
            help='This will list the languages in which the video is available instead of printing them',
        )

        parser.add_argument(
            "--exclude-generated",
            action="store_const",
            const=True,
            default=False,
            help="If this flag is set transcripts which have been generated by YouTube will not be retrieved.",
        )
        parser.add_argument(
            "--exclude-manually-created",
            action="store_const",
            const=True,
            default=False,
            help="If this flag is set transcripts which have been manually created will not be retrieved.",
        )
        parser.add_argument(
            "--translate",
            default="",
            help=(
                "The language code for the language you want this transcript to be translated to. Use the "
                "--list-transcripts feature to find out which languages are translatable and which translation "
                "languages are available."
            ),
        )

        return self._sanitize_video_ids(parser.parse_args(self._args))

    def _sanitize_video_ids(self, args):
        args.video_ids = [video_id.replace("\\", "") for video_id in args.video_ids]
        return args

    def _build_available_formats(self):
        # This method should be implemented to return the available formats
        # For now, we'll return an empty list as it's not provided in the original file or the new code block
        return []
