{{/*
Expand the namespace of the release.
Allows overriding.
*/}}
{{- define "kube_info.namespace" -}}
{{- default .Release.Namespace .Values.namespace -}}
{{- end -}}

{{/*
Expand the name of the chart.
*/}}
{{- define "kube_info.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}


{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "kube_info.fullname" -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- default (printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-") .Values.fullnameOverride -}}
{{- end -}}


{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "kube_info.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Set paths for images
*/}}
{{- define "kube_info.image" -}}
{{- if .Values.image.tag -}}
{{ .Values.image.repository }}:{{ .Values.image.tag }}
{{- else -}}
{{ .Values.image.repository }}:{{ .Chart.AppVersion }}
{{- end -}}
{{- end -}}

{{/*
Selector labels
*/}}
{{- define "kube_info.selectorLabels" -}}
app.kubernetes.io/name: {{ include "kube_info.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{/*
Create metalabels
*/}}
{{- define "kube_info.metaLabels" -}}
{{ include "kube_info.selectorLabels" . }}
helm.sh/chart: {{ template "kube_info.chart" . }}
app.kubernetes.io/managed-by: "{{ .Release.Service }}"
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- if .Values.metaLabels}}
{{ toYaml .Values.metaLabels }}
{{- end }}
{{- end -}}