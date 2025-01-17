package main

import (
	"errors"
	"io"
	"m3u8dl/utils"
	"os"
	"path/filepath"

	"github.com/grafov/m3u8"
)

func decode(input string) (*m3u8.MediaPlaylist, error) {
	var m3u8In io.ReadCloser
	if utils.IsValidUrl(input) {
		resp, err := httpGet(input)
		if err != nil {
			return nil, err
		}
		//m3u8In = resp.Body
		path:=filepath.Join(*flagTmpDir, "playlist.m3u8")
		f, e := os.Create(path)
		if e != nil {
			panic(e)
		}
		defer f.Close()
		//f.ReadFrom(resp.Body)
		io.Copy(f, resp.Body)
		m3u8In, err = os.Open(path)
		if err != nil {
			return nil, err
		}
	} else {
		var err error
		m3u8In, err = os.Open(input)
		if err != nil {
			return nil, err
		}
	}

	pl, listType, err := m3u8.DecodeFrom(m3u8In, true)
	m3u8In.Close()
	if err != nil {
		return nil, err
	}

	if listType != m3u8.MEDIA {
		return nil, errors.New("Please provide media file")
	}

	return pl.(*m3u8.MediaPlaylist), nil
}
