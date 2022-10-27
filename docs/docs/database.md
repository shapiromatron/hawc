# Database

The HAWC database is a [PostgreSQL](https://www.postgresql.org/) database. See diagrams for individual apps withing the larger HAWC project.

## Literature screening schema

<figure markdown>
  ![HAWC literature data schema](./static/img/hawc-schema-lit.jpeg)
  <figcaption>Study and literature schema. The image is very large; please save/or open in another tab.</figcaption>
</figure>

## Study and risk of bias schema

<figure markdown>
  ![HAWC study data schema](./static/img/hawc-schema-study.jpeg)
  <figcaption>Study and risk-of bias schema. The image is very large; please save/or open in another tab.</figcaption>
</figure>

## Animal bioassay schema

<figure markdown>
  ![HAWC animal bioassay data schema](./static/img/hawc-schema-animal.jpeg)
  <figcaption>Animal bioassay schema. The image is very large; please save/or open in another tab.</figcaption>
</figure>

<figure markdown>
  ![HAWC BMD data schema](./static/img/hawc-schema-bmd.jpeg)
  <figcaption>BMD schema. The image is very large; please save/or open in another tab.</figcaption>
</figure>

## Epidemiology schema

<figure markdown>
  ![HAWC epidemiology data schema](./static/img/hawc-schema-epi.jpeg)
  <figcaption>Epidemiology schema. The image is very large; please save/or open in another tab.</figcaption>
</figure>

<figure markdown>
  ![HAWC epidemiology v2 data schema](./static/img/hawc-schema-epiv2.jpeg)
  <figcaption>Epidemiology v2 schema. The image is very large; please save/or open in another tab.</figcaption>
</figure>

<figure markdown>
  ![HAWC epi meta analysis data schema](./static/img/hawc-schema-epimeta.jpeg)
  <figcaption>Epidemiology meta-analysis schema. The image is very large; please save/or open in another tab.</figcaption>
</figure>

## *In-vitro* data schema

<figure markdown>
  ![HAWC invitro data schema](./static/img/hawc-schema-invitro.jpeg)
  <figcaption>*In vitro* data schema. The image is very large; please save/or open in another tab.</figcaption>
</figure>

## *Vocabulary* schema

<figure markdown>
  ![HAWC controlled vocabulary schema](./static/img/hawc-schema-vocab.jpeg)
  <figcaption>Controlled vocabulary + ontology mapping data schema. The image is very large; please save/or open in another tab.</figcaption>
</figure>

## *Summary* schema

<figure markdown>
  ![HAWC summary data schema](./static/img/hawc-schema-summary.jpeg)
  <figcaption>Summary data schema. The image is very large; please save/or open in another tab.</figcaption>
</figure>

## Schema figure generation

To generate these database schema diagrams:

```bash
manage graph_models -g --pydot -o ./docs/docs/static/img/hawc-schema-lit.jpeg lit study
manage graph_models -g --pydot -o ./docs/docs/static/img/hawc-schema-study.jpeg study riskofbias
manage graph_models -g --pydot -o ./docs/docs/static/img/hawc-schema-animal.jpeg animal
manage graph_models -g --pydot -o ./docs/docs/static/img/hawc-schema-bmd.jpeg bmd
manage graph_models -g --pydot -o ./docs/docs/static/img/hawc-schema-epi.jpeg epi
manage graph_models -g --pydot -o ./docs/docs/static/img/hawc-schema-epiv2.jpeg epiv2
manage graph_models -g --pydot -o ./docs/docs/static/img/hawc-schema-epimeta.jpeg epimeta
manage graph_models -g --pydot -o ./docs/docs/static/img/hawc-schema-invitro.jpeg invitro
manage graph_models -g --pydot -o ./docs/docs/static/img/hawc-schema-vocab.jpeg vocab
manage graph_models -g --pydot -o ./docs/docs/static/img/hawc-schema-summary.jpeg summary
```
