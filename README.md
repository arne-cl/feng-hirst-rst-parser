# feng-hirst-rst-parser

This repository contains my fork of the RST parser published by
Vanessa Wei Feng and Graeme Hirst. I updated some of its dependencies,
dockerized the application, added some end-to-end tests and changed its
output format to make it simpler to parse (e.g. by [discoursegraphs](https://github.com/arne-cl/discoursegraphs)
or the [rst-converter-service](https://arne-cl@github.com/NLPbox/rst-converter-service).

The [original source code](http://www.cs.toronto.edu/~weifeng/software.html)
is still part of this repository. (The version published in Feng and Hirst (2012)
is tagged `1.01`, Feng and Hirst (2014) is tagged `2.01` -- both are
in the `master` branch. The original README is kept in the file
`README-original.txt`.)


# Installation

```
docker build -t feng-hirst .
```

# Usage

```
docker run --entrypoint=pytest -ti feng-hirst test_feng.py
```

If your input text is in `/tmp/input.txt`:

```
cat /tmp/input.txt
Although they didn't like it, they accepted the offer.
```

you can map the `/tmp` directory into the container and parse the text like
this:

```
docker run -v /tmp:/tmp -ti feng-hirst /tmp/input.txt
ParseTree('Contrast[S][N]', ["Although they did n't like it ,", 'they accepted the offer .'])
```

**NOTE**: For my convenience as a developer, this fork does not use the
original output, which looks like this:

```
(Contrast[S][N]
  _!Although they did n't like it ,!_
  _!they accepted the offer . <P>!_)
```

but the one seen above (based on / parsed by the Python nltk Tree implementation).