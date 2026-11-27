# SeeFix

Projects for fixes developed with visual verification, with reusable code,
assets, and a written method.

- [Stream Deck Plus](Stream-Deck-Plus/README.md): StreamController icon repair,
  OBS meter redraw fix, and an Omarchy shortcuts page.

Camera images, screenshots, screen recordings, application credentials, and
machine logs are excluded. Generated builds are ignored because they embed local
paths, device serials, and settings copied from the source OBS page. Keep custom
build output and private profiles outside this repository.

## Inspiration

The idea of checking a fix by looking at the device came from Omarchy community
posts that point laptops at mirrors. No code was taken from those posts.

## License

MIT, see [LICENSE](LICENSE). One file is an exception:
`Stream-Deck-Plus/patches/obs-meter-redraw.patch` modifies the StreamController
OBS plugin, which is GPL-3.0, and is offered under GPL-3.0. The plugins
themselves are referenced, not redistributed.
