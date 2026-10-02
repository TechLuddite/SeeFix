# Validation record

Observed on October 1, 2026, with the device/software in `provenance.json`.

- Camera checks confirmed all eight icons on both pages, the four shortcut dial
  instruction panels, and the repaired OBS audio meter panels.
- The user physically confirmed swipe navigation and the Terminal button worked.
- Both pages also passed the installed app's page-selection/readback API checks.
- Virtual-keyboard access passed a create/close UInput check.
- The configured shortcuts matched the installed Omarchy bindings. Remaining
  buttons were not all individually pressed during the session.
- The actual recorder process selected `-a default_output -ac aac` and contained
  no `default_input`. Recording start and clean stop succeeded.
- ffprobe confirmed a finalized 7.7-second H.264 video with AAC audio.
- Original OBS scene and dial action objects remained unchanged.
- Design review: 9/10. Functionality and usability review: 9.5/10. These are review
  judgments, supported by the checks above, rather than automated benchmarks.

OBS's websocket was not connected during testing, so live scene switching and
meter responsiveness to OBS input were not verified end to end. Meter images did
render after the fix. Camera blur prevented reading the small dynamic Record /
STOP REC caption; its settings and source behavior were checked.

Captured media, raw process logs, personal paths, credentials, and device serials
are deliberately not part of this project. Packaging checks additionally cover
portable generation, profile parsing, icon XML, patch idempotence, and absence of
captured media or local configuration in the published files.
