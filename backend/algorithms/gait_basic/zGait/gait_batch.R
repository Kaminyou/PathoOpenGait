

# function ----------------------------------------------------------------

BatchNoteGait <- function (batch.info, batch.id) {
  # Process raw batch information, 
  # and output table of round ids of each patient as log of batch.
  #
  # Args:
  #   batch.info: batch information with number of rounds and notes.
  #   batch.id: file name of batch information. 
  # 
  # Returns:
  #   batch data.
  
  # generate vector of all round ids
  for (i in 1:nrow(batch.info)) batch.info$round.ids[i] <- paste(c(1:batch.info$round.n[i]), collapse = ",")  # 1,2,3,4
  
  # remove failed round ids according to note
  batch.info$round.rmv <- "-"
  
  if (any(batch.info$note != "")) {
    
    batch.info$note <- gsub("\\(.*?\\)", "", batch.info$note)
    batch.info$note <- gsub("(^,\\s)|(,\\s$)", "", batch.info$note)
    # batch.info$note <- gsub(",*\\s*\\(.*?\\),*\\s*", "", batch.info$note)
    
    batch.info$round.rmv <- gsub("[^#0-9]", "", batch.info$note)  # #1#2#3#4
    
    for (i in 1:nrow(batch.info)) {
      
      if (batch.info$round.rmv[i] == "") next 
      
      round.ids <- unlist(strsplit(batch.info$round.ids[i], split = ","))
      round.rmv <- unlist(strsplit(batch.info$round.rmv[i], split = "#"))
      
      if (tail(round.rmv, n = 1) > batch.info$round.n[i]) 
        stop (paste(batch.info$yyyy, batch.info$mm, batch.info$dd, batch.info$id, sep = "-"), "round ids error")  # yyyy-mm-dd-n
      
      round.ids <- round.ids[!(round.ids %in% round.rmv)]
      
      batch.info$round.ids[i] <- paste(round.ids, collapse = ",")  # 1,2,3,4
      
    }
    
  } 
  
  # set batch data with patient ids, round ids, removed round ids
  batch <- data.frame(pt.id = paste(batch.info$yyyy, batch.info$mm, batch.info$dd, batch.info$id, sep = "-"),  # yyyy-mm-dd-n
                      round.ids = batch.info$round.ids, 
                      round.rmv = batch.info$round.rmv, 
                      stringsAsFactors = FALSE)
  
  # output batch data
  IOGait(io.type = "write", gait.path = FilePathGait(path.type = "batch", batch.id), batch)
  
  # show batch data in the console
  cat("\n")
  print(batch)
  cat("\n")
  
  return (batch)
  
}

IOGait <- function (io.type, gait.path, gait.data = NULL) {
  # Manage read and write gait data.
  #
  # Args:
  #   io.type: type of function, which can be "read" or "write".
  #   gait.path: file path generated from DirGait function. 
  #   gait.data: data to write, when io.type is "write".
  # 
  # Returns: 
  #   gait data, when io.type is "read".
  
  switch (io.type, 
          read = {
            
            return (read.csv(gait.path, header = FALSE)[, 1:(1+6)])
            
          }, 
          write = {
            
            write.csv(gait.data, gait.path, row.names = FALSE)
            
          })
  
}

SetWDGait <- function (set.dir.type, pt.id) {
  # set working directory into folder of individual patient or set it back to the source, 
  # 
  # Args:
  #   gait.dir.type: type of directory, which can be "set" or "set.back".
  
  if (set.dir.type == "set") {
    
    if (!(dir.exists(paste(getwd(), "output", pt.id, sep = "/")))) {
      
      dir.create(paste(getwd(), "output", pt.id, sep = "/"))
      setwd(paste(getwd(), "output", pt.id, sep = "/"))
      
      dir.create(paste(getwd(), "00_raw", sep = "/"))
      dir.create(paste(getwd(), "0_clean", sep = "/"))
      dir.create(paste(getwd(), "1_stride", sep = "/"))
      
    } else setwd(paste(getwd(), "output", pt.id, sep = "/"))
    
  } else if (set.dir.type == "set.back") setwd(dirname(dirname(getwd())))
  
}

FilePathGait <- function (path.type, data.id = NULL, gait.data.type = NULL, gait.data.leg = NULL) {
  # Generate file path.
  #
  # Args:
  #   gait.dir.type: type of directory, which can be "batch", "read", "write", "plot".
  #   data.id: id of data (yyyy-mm-dd-n-n).
  #   gait.data.type: type of gait data, 
  #                   which can be "raw", "clean", "stride", "summary", when gait.dir.type is "write";  
  #                   which can be "raw", "clean", "smooth", "state", "slice", "step", "stride", "summary", when gait.dir.type is "plot".
  #   gait.data.leg: specific leg to plot, can be "left", "right", or "both", 
  #                  can be used only when gait.dir.type is "plot".
  # 
  # Returns: 
  #   file path, when gait.dir.type is "batch", "read", "write", or "plot".
  
  # set folder path
  gait.dir <- getwd()
  
  gait.dir <- 
    switch (path.type, 
            batch = paste(gait.dir, "output", "batch_log", sep = "/"), 
            read = gsub("output", "input", gait.dir), 
            write = gait.dir, 
            plot = gait.dir)
  
  if (path.type == "write")
    if (gait.data.type != "summary") 
      gait.dir <- paste(gait.dir,
                        switch (gait.data.type,
                                raw = "00_raw",
                                clean = "0_clean",
                                stride = "1_stride"),
                        sep = "/")
  
  if (path.type == "plot") 
    gait.dir <- paste(gait.dir, 
                      switch (gait.data.leg, 
                              both = "000_pic", 
                              left = "000_pic_left", 
                              right = "000_pic_right"), 
                      sep = "/")
  
  # set file name and type
  gait.base <-
    switch (path.type,
            batch = data.id,
            read = data.id,
            write = data.id,
            plot = paste(data.id,
                         switch (gait.data.type,
                                 raw = "00",
                                 clean = "0",
                                 smooth = "1",
                                 state = "2",
                                 slice = "3",
                                 step = "4",
                                 stride = "5",
                                 summary = "6"),
                         gait.data.type,
                         sep = "_"))
  
  if (path.type == "write")
    if (gait.data.type == "summary")
      gait.base <- switch (gait.data.leg, 
                           both = gait.base, 
                           left = paste(gait.base, "left", sep = "_"), 
                           right = paste(gait.base, "right", sep = "_"))
  
  gait.base <- 
    switch (path.type, 
            batch = paste(gait.base, "csv", sep = "."), 
            read = paste(gait.base, "csv", sep = "."), 
            write = paste(gait.base, "csv", sep = "."), 
            plot = paste(gait.base, "png", sep = "."))
  
  # generate file path
  gait.path <- paste(gait.dir, gait.base, sep = "/")
  
  return (gait.path)  
  
}

MsgGait <- function (data.id, gait.data, msg.type) {
  # Show message of suspicious error in gait data.
  #
  # Args:
  #   data.id: id of data (yyyy-mm-dd-n-n).
  #   gait.data: data to process. 
  #   gait.data.type: type of gait plot, 
  #                   which can be "step", "stride", "summary".
  
  switch (msg.type, 
          too.many.x.outliers = {
            
            x.mid.75 <- quantile(gait.data$x.mid, probs = 0.75)
            x.mid.25 <- quantile(gait.data$x.mid, probs = 0.25)
            x.mid.iqr <- x.mid.75 - x.mid.25
            x.mid.ulm <- x.mid.75 + x.mid.iqr * 1.5
            x.mid.llm <- x.mid.25 - x.mid.iqr * 1.5
            
            if (length(which((gait.data$x.mid > x.mid.ulm) | 
                             (gait.data$x.mid < x.mid.llm))) > (nrow(gait.data) * 0.05)) cat(data.id, "clean: over 5% x outliers", "\n")
            
          }, 
          too.far = {
            
            dt.ulm <- 7000
            
            if (length(which((gait.data$left.dt > dt.ulm) | 
                             (gait.data$right.df > dt.ulm))) > (nrow(gait.data) * 0.05)) cat(data.id, "clean: over 5% depth >", dt.ulm, "\n")
            
          }, 
          no.turn = {
            
            if (!(nrow(gait.data) > 0)) cat(data.id, "state: no turn", "\n")
            
          }, 
          no.state = {
            
            forth.gait.data <- gait.data[gait.data$direction == "forth", ]
            back.gait.data <- gait.data[gait.data$direction == "back", ]
            
            if (!any(forth.gait.data$state == "straight")) stop (data.id, " state: no forth straight", "\n")
            if (!any(back.gait.data$state == "straight")) stop (data.id, " state: no back straight", "\n")
            
            if (!any(forth.gait.data$state == "turn")) stop (data.id, " state: no forth turn", "\n")
            if (!any(back.gait.data$state == "turn")) stop (data.id, " state: no back turn", "\n")
            
            if (!any(forth.gait.data$state == "buffer")) stop (data.id, " state: no forth buffer", "\n")
            if (!any(back.gait.data$state == "buffer")) stop (data.id, " state: no back buffer", "\n")
            
          }, 
          no.step = {
            
            if (!any(gait.data$step.leg == "left")) cat(data.id, "step: no left step", "\n")
            if (!any(gait.data$step.leg == "right")) cat(data.id, "step: no right step", "\n")
            
          }, 
          no.stride = {
            
            if (!any(gait.data$left.stride.lt > 0)) cat(data.id, "stride: no left stride", "\n")
            if (!any(gait.data$right.stride.lt > 0)) cat(data.id, "stride: no right stride", "\n")
            
          },
          no.summary = {
            
            if (!(gait.data$left.size > 0)) cat(data.id, "summary: no left stride", "\n")
            if (!(gait.data$right.size > 0)) cat(data.id, "summary: no right stride", "\n")
            
          })
  
}

RawCleanGait <- function (data.id) {
  # Exclude invalid values and background noise, 
  # and output table and plot of clean data.
  #
  # Args:
  #   data.id: id of raw data (yyyy-mm-dd-n-n).
  #
  # Returns:
  #   clean data.
  
  # set raw data
  gait.data.raw <- IOGait(io.type = "read", 
                          gait.path = FilePathGait(path.type = "read", data.id = data.id))
  
  names(gait.data.raw) <- c("time",
                            "left.y", "left.x", "left.dt",
                            "right.y", "right.x", "right.dt")  
  
  gait.data.raw$x.mid <- (gait.data.raw$left.x + gait.data.raw$right.x) / 2
  gait.data.raw$dt.mid <- (gait.data.raw$left.dt + gait.data.raw$right.dt) / 2
  
  # write raw data
  IOGait(io.type = "write", 
         gait.path = FilePathGait(path.type = "write", data.id = data.id, gait.data.type = "raw"), 
         gait.data = gait.data.raw)
    
  # exclude invalid values
  gait.data.clean <- na.omit(gait.data.raw)  # omit NA
  gait.data.clean <- gait.data.clean[gait.data.clean$left.dt > 0, ]  # exclude zero depth
  gait.data.clean <- gait.data.clean[gait.data.clean$right.dt > 0, ]  # exclude zero depth
  gait.data.clean <- gait.data.clean[gait.data.clean$time != 0, ]  # exclude zero time
  
  MsgGait(data.id = data.id, gait.data = gait.data.clean, msg.type = "too.many.x.outliers")
  MsgGait(data.id = data.id, gait.data = gait.data.clean, msg.type = "too.far")
  
  # TODO try regression
  # exclude background noise
  x.mid.75 <- quantile(gait.data.clean$x.mid, probs = 0.75)
  x.mid.25 <- quantile(gait.data.clean$x.mid, probs = 0.25)
  x.mid.iqr <- x.mid.75 - x.mid.25
  x.mid.ulm <- x.mid.75 + x.mid.iqr * 1.5
  x.mid.llm <- x.mid.25 - x.mid.iqr * 1.5
  
  gait.data.clean <- gait.data.clean[(gait.data.clean$x.mid <= x.mid.ulm) &
                                       (gait.data.clean$x.mid >= x.mid.llm), ]
  
  dt.mid.ulm <- 7000
  
  gait.data.clean <- gait.data.clean[gait.data.clean$dt.mid <= dt.mid.ulm, ]
  
  dt.mid.ulm <- 6000
  
  time.05 <- as.numeric(quantile(gait.data.clean$time, probs = 0.05))
  time.95 <- as.numeric(quantile(gait.data.clean$time, probs = 0.95))
  
  gait.data.clean <- gait.data.clean[((gait.data.clean$time < time.05) & 
                                        (gait.data.clean$dt.mid < dt.mid.ulm)) | 
                                       ((gait.data.clean$time > time.95) & 
                                          (gait.data.clean$dt.mid < dt.mid.ulm)) | 
                                       ((gait.data.clean$time >= time.05) & 
                                          (gait.data.clean$time <= time.95)), ]
  
  # write clean data
  IOGait(io.type = "write", 
         gait.path = FilePathGait(path.type = "write", data.id = data.id, gait.data.type = "clean"), 
         gait.data = gait.data.clean)
  
  return (gait.data.clean)
  
}

SmoothGait <- function (data.id, gait.data.clean, smooth.window = 5) {
  # Smooth data, 
  # and output plot of smooth data.
  #
  # Args:
  #   data.id: id of clean data (yyyy-mm-dd-n-n).
  #   gait.data.clean: clean data. 
  #   smooth.window: width of window for running median smoothing, default is 5. 
  #
  # Returns:
  #   smooth data.
  
  # set smooth data
  gait.data.smooth <- data.frame(gait.data.clean, 
                                 left.x.smooth = 0, 
                                 right.x.smooth = 0, 
                                 left.dt.smooth = 0, 
                                 right.dt.smooth = 0)
  
  # smooth noise
  gait.data.smooth$left.x.smooth <- c(runmed(gait.data.smooth$left.x, k = smooth.window))
  gait.data.smooth$right.x.smooth <- c(runmed(gait.data.smooth$right.x, k = smooth.window))
  gait.data.smooth$left.dt.smooth <- c(runmed(gait.data.smooth$left.dt, k = smooth.window))
  gait.data.smooth$right.dt.smooth <- c(runmed(gait.data.smooth$right.dt, k = smooth.window))
  
  return (gait.data.smooth)
  
}

stateGait <- function (data.id, gait.data.smooth, buffer.window = 3) {
  # Indicate walking state for smooth data, 
  # and output plot of state data.
  #
  # Args:
  #   data.id: id of smooth data (yyyy-mm-dd-n-n).
  #   gait.data.smooth: smooth data.
  #   buffer.window: width of window for buffering the turning state, default is 3.
  #
  # Returns:
  #   state data.
  
  # set state data
  gait.data.state <- data.frame(gait.data.smooth, 
                                dx = gait.data.smooth$left.x.smooth - gait.data.smooth$right.x.smooth, 
                                wt = abs(gait.data.smooth$left.x.smooth - gait.data.smooth$right.x.smooth), 
                                direction = "-", 
                                state = "-", 
                                left.dt.inverse = gait.data.smooth$left.dt.smooth, 
                                right.dt.inverse = gait.data.smooth$right.dt.smooth)
  
  # assign direction
  dt.mid.75 <- as.numeric(quantile(gait.data.state$dt.mid, probs = 0.75))
  wt.25 <- as.numeric(quantile(gait.data.state$wt, probs = 0.25))
  wt.10 <- as.numeric(quantile(gait.data.state$wt, probs = 0.10))
  
  turn <- gait.data.state[(gait.data.state$dt.mid > dt.mid.75) &
                            (gait.data.state$wt < wt.10), ]
  
  MsgGait(data.id = data.id, gait.data = turn, msg.type = "no.turn")
  
  if (!(nrow(turn) > 0)) {
    
    dt.mid.95 <- as.numeric(quantile(gait.data.state$dt.mid, probs = 0.95))
    
    turn <- gait.data.state[gait.data.state$dt.mid > dt.mid.95, ]
    
  }
  
  turn.time <- turn$time[which.min((rank(-turn$dt.mid, ties.method = "first") + 
                                      rank(turn$wt, ties.method = "first")))]
  
  levels(gait.data.state$direction) <- c("-", "forth", "back")
  gait.data.state$direction[gait.data.state$time < turn.time] <- "forth"
  gait.data.state$direction[gait.data.state$time >= turn.time] <- "back"
  # gait.data.state$direction <- ifelse(gait.data.state$time < turn.time, "forth", "back")
  
  # check flip
  flip <- gait.data.state[((gait.data.state$dx < 0) & 
                             (gait.data.state$direction == "forth")) | 
                            ((gait.data.state$dx > 0) & 
                               (gait.data.state$direction == "back")), ]
  
  if (nrow(flip) > 0) {
    
    gait.data.state$left.x.smooth[gait.data.state$time %in% flip$time] <- flip$right.x.smooth
    gait.data.state$right.x.smooth[gait.data.state$time %in% flip$time] <- flip$left.x.smooth
    
    gait.data.state$dx[gait.data.state$time %in% flip$time] <- -flip$dx
    
    gait.data.state$left.y[gait.data.state$time %in% flip$time] <- flip$right.y
    gait.data.state$right.y[gait.data.state$time %in% flip$time] <- flip$left.y
    
    gait.data.state$left.dt.smooth[gait.data.state$time %in% flip$time] <- flip$right.dt.smooth
    gait.data.state$right.dt.smooth[gait.data.state$time %in% flip$time] <- flip$left.dt.smooth
    
  }
  
  # assign state
  forth.dx.mu <- mean(gait.data.state$dx[gait.data.state$direction == "forth"])
  back.dx.mu <- mean(gait.data.state$dx[gait.data.state$direction == "back"])
  
  levels(gait.data.state$state) <- c("-", "straight", "turn", "buffer")
  gait.data.state$state[(gait.data.state$dx < forth.dx.mu) & 
                          (gait.data.state$dx > back.dx.mu) & 
                          (gait.data.state$dt.mid > dt.mid.75) & 
                          (gait.data.state$wt < wt.25)] <- "turn"
  
  straight <- gait.data.state[gait.data.state$state != "turn", ]
  
  forth.straight.tail <- max(straight$time[straight$direction == "forth"])
  back.straight.head <- min(straight$time[straight$direction == "back"])
  
  gait.data.state$state[(gait.data.state$time > forth.straight.tail) & 
                          (gait.data.state$time < back.straight.head)] <- "turn"
  gait.data.state$state[(gait.data.state$time <= forth.straight.tail) | 
                          (gait.data.state$time >= back.straight.head)] <- "straight"
  
  # buffer turning
  if (!any((gait.data.state$direction == "forth") && 
           (gait.data.state$state == "turn"))) gait.data.state$state[max(which(gait.data.state$direction == "forth"))] <- "turn" 
  if (!any((gait.data.state$direction == "back") && 
           (gait.data.state$state == "turn"))) gait.data.state$state[min(which(gait.data.state$direction == "back"))] <- "turn"
  
  straight <- gait.data.state[gait.data.state$state == "straight", ]
  
  forth.turn.dt.mid.llm <- min(tail(straight$dt.mid[straight$direction == "forth"], n = buffer.window + 1))
  back.turn.dt.mid.llm <- min(head(straight$dt.mid[straight$direction == "back"], n = buffer.window + 1))
  
  gait.data.state$state[(((gait.data.state$direction == "forth") & 
                            (gait.data.state$dt.mid > forth.turn.dt.mid.llm)) | 
                           ((gait.data.state$direction == "back") & 
                              (gait.data.state$dt.mid > back.turn.dt.mid.llm))) & 
                          (gait.data.state$state == "straight")] <- "buffer"
  
  buffer <- gait.data.state[gait.data.state$state == "buffer", ]
  
  gait.data.state$state[(gait.data.state$time >= min(buffer$time)) & 
                          (gait.data.state$time <= max(buffer$time)) & 
                          (gait.data.state$state != "turn")] <- "buffer"
  
  MsgGait(data.id = data.id, gait.data = gait.data.state, msg.type = "no.state")
  
  # inverse back depth 
  turn.dt <- max(turn$left.dt.smooth, turn$right.dt.smooth)
  
  gait.data.state$left.dt.inverse[gait.data.state$direction == "back"] <- 
    turn.dt - gait.data.state$left.dt.inverse[gait.data.state$direction == "back"]
  gait.data.state$right.dt.inverse[gait.data.state$direction == "back"] <- 
    turn.dt - gait.data.state$right.dt.inverse[gait.data.state$direction == "back"]
  
  return (gait.data.state)
  
}

SliceGait <- function(data.id, gait.data.state, time.gap.ulm = 1000/30 * 7, slice.time.lt.llm = 1000/30 * 8) {
  # Assign slice ids, 
  # and output plot of slice data.
  #
  # Args:
  #   data.id: ids of state data (yyyy-mm-dd-n-n).
  #   gait.data.state: state data.
  #   time.gap.ulm: upper limit of gap between two slices, 
  #                 recording rate is 30 frame per second, 
  #                 simplest model for calculating a stance phase is a 2nd degree polynomial line, 
  #                 3 points determine a 2nd degree polynomial line, 
  #                 2 missing stance phases determine a break, 
  #                 a break include 3 * 2 = 6 missing frames, which is 6 + 1 = 7 frame gaps, 
  #                 default is 1000/30 * (3 * 2 + 1) = 1000/30 * 7 = 233.
  #   slice.time.lt.llm: lower limit of length of a slice, 
  #                      recording rate is 30 frame per second, 
  #                      simplest model for calculating a stance phase is a 2nd degree polynomial line, 
  #                      3 points determine a 2nd degree polynomial line,
  #                      2 same-leg stance phases determine a stride, which shall be nested by an other-leg stance phase, 
  #                      a stride include 3 * 3 = 9 frames, which is 9 - 1 = 8 frame gaps, 
  #                      default is 1000/30 * (3 * 3 - 1) = 1000/30 * 8 = 267. 
  #                    
  # Returns:
  #   slice data.
  
  # set slice data
  gait.data.slice <- data.frame(gait.data.state, 
                                time.gap = 0, 
                                dt.mid.gap = 0, 
                                slice.id = -1)
  
  gait.data.slice$time.gap[-nrow(gait.data.slice)] <- gait.data.state$time[-1] - gait.data.state$time[-nrow(gait.data.state)]
  gait.data.slice$dt.mid.gap[-nrow(gait.data.slice)] <- gait.data.state$dt.mid[-1] - gait.data.state$dt.mid[-nrow(gait.data.state)]
  
  # cut at time gap
  time.gaps.indexes <- unique(c(which(gait.data.slice$time.gap > time.gap.ulm), 
                                max(which((gait.data.slice$direction == "forth") & 
                                            (gait.data.slice$state == "straight"))), 
                                max(which(gait.data.slice$direction == "forth")), 
                                max(which(gait.data.slice$state == "buffer"))))
  
  time.gaps.indexes <- sort(unique(time.gaps.indexes))
  
  slice.time.df <- data.frame(head = c(head(gait.data.slice$time, n = 1),
                                       gait.data.slice$time[time.gaps.indexes + 1]), 
                              tail = c(gait.data.slice$time[time.gaps.indexes], 
                                       tail(gait.data.slice$time, n = 1)))
  
  # cut at depth gap due to break of recording
  straight.dt.mid.gap <- gait.data.slice$dt.mid.gap[gait.data.slice$state == "straight"]
  
  straight.dt.mid.gap.75 <- as.numeric(quantile(straight.dt.mid.gap, probs = 0.75))
  straight.dt.mid.gap.25 <- as.numeric(quantile(straight.dt.mid.gap, probs = 0.25))
  straight.dt.mid.gap.iqr <- straight.dt.mid.gap.75 - straight.dt.mid.gap.25
  straight.dt.mid.gap.ulm <- straight.dt.mid.gap.75 + straight.dt.mid.gap.iqr * 3
  straight.dt.mid.gap.llm <- straight.dt.mid.gap.25 - straight.dt.mid.gap.iqr * 3
  
  dt.mid.gap.slice.time.df <- data.frame(head = slice.time.df$head,
                                         tail = ifelse((slice.time.df$head + time.gap.ulm * 1.5) < slice.time.df$tail,
                                                       slice.time.df$head + time.gap.ulm * 1.5,
                                                       slice.time.df$tail))
  
  for (j in 1:nrow(dt.mid.gap.slice.time.df)) {
    
    dt.mid.gap.slice.time <- dt.mid.gap.slice.time.df[j, ]
    
    dt.mid.gap.slice <- gait.data.slice[(gait.data.slice$time >= dt.mid.gap.slice.time$head) & 
                                          (gait.data.slice$time <= dt.mid.gap.slice.time$tail), ]
    
    if ((max(dt.mid.gap.slice$dt.mid.gap) >= straight.dt.mid.gap.llm) &
        (min(dt.mid.gap.slice$dt.mid.gap) <= straight.dt.mid.gap.ulm)) next 
    
    dt.mid.gap.index <- max(which((dt.mid.gap.slice$dt.mid.gap > straight.dt.mid.gap.ulm) | 
                                    (dt.mid.gap.slice$dt.mid.gap < straight.dt.mid.gap.llm)))
    
    if (dt.mid.gap.index == nrow(dt.mid.gap.slice)) dt.mid.gap.index <- dt.mid.gap.index - 1
    
    slice.time.df$head[slice.time.df$head == dt.mid.gap.slice.time$head] <- min(dt.mid.gap.slice$time[dt.mid.gap.index + 1])
    
  }
  
  # re-connect continued slices
  slice.time.df$direction <- gait.data.slice$direction[gait.data.slice$time %in% slice.time.df$head]
  slice.time.df$state <- gait.data.slice$state[gait.data.slice$time %in% slice.time.df$head]
  slice.time.df$slice.gap <- -1
  slice.time.df$slice.gap[-nrow(slice.time.df)] <- slice.time.df$head[-1] - slice.time.df$tail[-nrow(slice.time.df)]
  
  cat.slice.time.df <- slice.time.df
  
  for (j in 1:(nrow(cat.slice.time.df) - 1)) {
    
    cat.slice.time1 <- cat.slice.time.df[j, ]
    cat.slice.time2 <- cat.slice.time.df[j + 1, ]
    
    if (cat.slice.time1$direction != cat.slice.time2$direction) next
    
    if (((cat.slice.time1$state == "turn") | 
         (cat.slice.time1$state == "buffer")) | 
        ((cat.slice.time2$state == "turn") | 
         (cat.slice.time2$state == "buffer"))) next 
    
    if (cat.slice.time1$slice.gap > time.gap.ulm * 1.5) next
    
    cat.slice.dt.mid.gap <- 
      gait.data.slice$dt.mid[gait.data.slice$time == cat.slice.time2$head] - gait.data.slice$dt.mid[gait.data.slice$time == cat.slice.time1$tail]
    
    if ((cat.slice.dt.mid.gap > straight.dt.mid.gap.ulm) | 
        (cat.slice.dt.mid.gap < straight.dt.mid.gap.llm)) next
    
    slice.time.df <- slice.time.df[slice.time.df$tail != cat.slice.time1$tail, ]
    
    slice.time.df$head[slice.time.df$head == cat.slice.time2$head] <- cat.slice.time1$head
    
    cat.slice.time.df$head[cat.slice.time.df$head == cat.slice.time2$head] <- cat.slice.time1$head
    
  }
  
  # exclude trivial slice
  slice.time.df$slice.time.lt <- slice.time.df$tail - slice.time.df$head
  
  slice.time.df <- slice.time.df[slice.time.df$slice.time.lt >= slice.time.lt.llm, ]
  
  # assign slice ids
  for (j in 1:nrow(slice.time.df)) {
    
    slice.time <- slice.time.df[j, ]
    
    gait.data.slice$slice.id[(gait.data.slice$time >= slice.time$head) & 
                               (gait.data.slice$time <= slice.time$tail)] <- j
    
  }
  
  return (gait.data.slice)
  
}

StepGait <- function (data.id, gait.data.slice, runs.window = 5, step.time.gap.ulm = 1000/30 * 2) {
  # Assign step ids, 
  # and output plot of step data.
  #
  # Args:
  #   data.id: id of slice data (yyyy-mm-dd-n-n).
  #   gait.data.slice: slcie data. 
  #   runs.window: width of window of runs, must be an odd number, default is 5.
  #   step.time.gap.ulm: lower limit of length of a step time for calculating a stance phase, 
  #                      recording rate is 30 frame per second, 
  #                      simplest model for calculating a stance phase is a 2nd degree polynomial line, 
  #                      3 points determine a 2nd degree polynomial line, 
  #                      a stance phase include 3 frames, which is 3 - 1 = 2 frame gaps, 
  #                      default is 1000/30 * (3 - 1) = 1000/30 * 2 = 67.
  # 
  # Returns:
  #   step data.
  
  gait.data.step <- data.frame(gait.data.slice, 
                               ddt = gait.data.slice$left.dt.inverse - gait.data.slice$right.dt.inverse, 
                               ddt.adj = 0, 
                               ddt.adj.leg = "left", 
                               ddt.adj.dif = 0, 
                               rhythm = "-", 
                               step.id = -1, 
                               step.leg = "-")
  
  # calibrate step length (difference of depth between two legs)
  forth.ddt.mu <- mean(gait.data.step$ddt[gait.data.step$direction == "forth"])
  back.ddt.mu <- mean(gait.data.step$ddt[gait.data.step$direction == "back"])
  
  gait.data.step$ddt.adj[gait.data.step$direction == "forth"] <- 
    gait.data.step$ddt[gait.data.step$direction == "forth"] - forth.ddt.mu
  gait.data.step$ddt.adj[gait.data.step$direction == "back"] <- 
    gait.data.step$ddt[gait.data.step$direction == "back"] - back.ddt.mu
  
  gait.data.step$ddt.adj.dif <- 0
  
  gait.data.step$ddt.adj.dif[-nrow(gait.data.step)] <- 
    (gait.data.step$ddt.adj[-1] - gait.data.step$ddt.adj[-nrow(gait.data.step)]) / 
    (gait.data.step$time[-1] - gait.data.step$time[-nrow(gait.data.step)])
  
  # extract step time
  step.ddt.adj.leg <- ifelse(gait.data.step$ddt.adj > 0, "left", "right")
  
  step.ddt.adj.leg.mx <- matrix(step.ddt.adj.leg, 
                                nrow = length(step.ddt.adj.leg), 
                                ncol = runs.window)
  
  ddt.adj.shift <- c(1:runs.window) - median(c(1:runs.window))
  
  for (j in 1:runs.window) {
    
    j.shift <- ddt.adj.shift[j]
    
    if (j.shift == 0) next
    
    if (j.shift < 0) step.ddt.adj.leg.mx[, j] <- c(tail(step.ddt.adj.leg, n = j.shift), 
                                                   rep(tail(step.ddt.adj.leg, n = 1), times = abs(j.shift)))
    
    if (j.shift > 0) step.ddt.adj.leg.mx[, j] <- c(rep(head(step.ddt.adj.leg, n = 1), times = j.shift), 
                                                   head(step.ddt.adj.leg, n = -j.shift))
    
  }
  
  levels(gait.data.step$ddt.adj.leg) <- c("left", "right")
  for (k in 1:length(step.ddt.adj.leg)) gait.data.step$ddt.adj.leg[k] <- names(which.max(table(step.ddt.adj.leg.mx[k, ])))
  
  slice <- gait.data.step[gait.data.step$slice.id > 0, ]
  
  step.time.indexes <- which(slice$ddt.adj.leg[-1] != slice$ddt.adj.leg[-nrow(slice)])
  
  for (j in 1:(max(slice$slice.id) - 1)) 
    step.time.indexes <- c(step.time.indexes, 
                           max(which(slice$slice.id == j)))
  
  step.time.indexes <- unique(step.time.indexes)
  
  step.time.indexes <- sort(step.time.indexes)
  
  step.time.df <- data.frame(head = c(head(slice$time, n = 1), 
                                      slice$time[step.time.indexes + 1]), 
                             tail = c(slice$time[step.time.indexes], 
                                      tail(slice$time, n = 1)), 
                             direction = slice$direction[c(step.time.indexes, nrow(slice))], 
                             state = slice$state[c(step.time.indexes, nrow(slice))], 
                             slice.id = slice$slice.id[c(step.time.indexes, nrow(slice))], 
                             step.leg = slice$ddt.adj.leg[c(step.time.indexes, nrow(slice))])
  
  # check initiation
  straight.slice <- gait.data.step[(gait.data.step$state == "straight") & 
                                     (gait.data.step$slice.id > 0), ]
  
  left.forth.ddt.adj.mu <- mean(straight.slice$ddt.adj[straight.slice$ddt.adj.leg == "left"])
  right.forth.ddt.adj.mu <- mean(straight.slice$ddt.adj[straight.slice$ddt.adj.leg == "right"])
  
  straight.step.time.df <- step.time.df[step.time.df$state == "straight", ]
  
  j <- 1
  repeat {
    
    start.step.time <- straight.step.time.df[j, ]
    
    start.step <- straight.slice[(straight.slice$time >= start.step.time$head) &
                                   (straight.slice$time <= start.step.time$tail), ]
    
    stand.step <- gait.data.step[gait.data.step$time < start.step.time$head, ]
    
    start.step.leg <- as.character(start.step.time$step.leg)
    
    if (switch (start.step.leg, 
                left = max(start.step$ddt.adj) > left.forth.ddt.adj.mu, 
                right = min(start.step$ddt.adj) < right.forth.ddt.adj.mu)) {
      
      start.step.ddt.adj.dif.exm <- 
        switch (start.step.leg, 
                left = as.numeric(quantile(start.step$ddt.adj.dif, probs = 0.95)), 
                right = as.numeric(quantile(start.step$ddt.adj.dif, probs = 0.05)))
      
      start.step.ddt.adj.dif.exm.time <- 
        switch (start.step.leg, 
                left = min(start.step$time[which(start.step$ddt.adj.dif >= start.step.ddt.adj.dif.exm)]), 
                right = min(start.step$time[which(start.step$ddt.adj.dif <= start.step.ddt.adj.dif.exm)]))
      
      start.step.stand <- start.step[start.step$time < start.step.ddt.adj.dif.exm.time, ]
      
      if (nrow(start.step.stand) > 0) {
        
        if ((max(start.step.stand$ddt.adj.dif) > 0) &
            (min(start.step.stand$ddt.adj.dif) < 0)) {
          
          start.step.stand.ddt.adj.dif.75 <- as.numeric(quantile(start.step.stand$ddt.adj.dif, probs = 0.75))
          start.step.stand.ddt.adj.dif.25 <- as.numeric(quantile(start.step.stand$ddt.adj.dif, probs = 0.25))
          start.step.stand.ddt.adj.dif.iqr <- start.step.stand.ddt.adj.dif.75 - start.step.stand.ddt.adj.dif.25
          
          start.step.stand.ddt.adj.dif.lmt <- 
            switch (start.step.leg, 
                    left = start.step.stand.ddt.adj.dif.75 + start.step.stand.ddt.adj.dif.iqr * 1.5, 
                    right = start.step.stand.ddt.adj.dif.25 - start.step.stand.ddt.adj.dif.iqr * 1.5)
          
          stand.step.time.tail.new <- 
            switch (start.step.leg, 
                    left = max(start.step.stand$time[start.step.stand$ddt.adj.dif <= start.step.stand.ddt.adj.dif.lmt]), 
                    right = max(start.step.stand$time[start.step.stand$ddt.adj.dif >= start.step.stand.ddt.adj.dif.lmt]))
          
          start.step.time.head.new <- min(start.step$time[start.step$time > stand.step.time.tail.new])
          
          step.time.df$head[step.time.df$head == start.step.time$head] <- start.step.time.head.new
          straight.step.time.df$head[straight.step.time.df$head == start.step.time$head] <- start.step.time.head.new
          
          start.step.time$head <- start.step.time.head.new
          
          start.step <- straight.slice[(straight.slice$time >= start.step.time$head) &
                                         (straight.slice$time <= start.step.time$tail), ]
          
          stand.step <- gait.data.step[gait.data.step$time < start.step.time$head, ]  
          
        }
        
      }
      
      if (!(nrow(stand.step) > 1)) break
      
      if ((max(stand.step$ddt.adj) > left.forth.ddt.adj.mu) | 
          (min(stand.step$ddt.adj) < right.forth.ddt.adj.mu)) break
      
      if (!((max(stand.step$ddt.adj.dif) > 0) &
            (min(stand.step$ddt.adj.dif) < 0))) break
      
      if ((max(stand.step$ddt.adj.dif) > 1) &
          (min(stand.step$ddt.adj.dif) < -1)) break
      
      gait.data.step$step.id[gait.data.step$time < start.step.time$head] <- 0
      
      break
      
    } else step.time.df <- step.time.df[step.time.df$head != start.step.time$head, ]
    
    j <- j + 1
    
  }
  
  # check length 
  step.time.df$step.time.lt <- step.time.df$tail - step.time.df$head
  
  straight.step.time.df <- step.time.df[step.time.df$state == "straight", ]
  
  left.step.time.lts <- straight.step.time.df$step.time.lt[straight.step.time.df$step.leg == "left"]
  right.step.time.lts <- straight.step.time.df$step.time.lt[straight.step.time.df$step.leg == "right"]
  
  left.step.time.lts.75 <- as.numeric(quantile(left.step.time.lts, probs = 0.75))
  left.step.time.lts.25 <- as.numeric(quantile(left.step.time.lts, probs = 0.25))
  left.step.time.lts.iqr <- left.step.time.lts.75 - left.step.time.lts.25
  left.step.time.lts.ulm <- left.step.time.lts.75 + left.step.time.lts.iqr * 1.5
  left.step.time.lts.llm <- left.step.time.lts.25 - left.step.time.lts.iqr * 1.5
  if (left.step.time.lts.llm < step.time.gap.ulm) left.step.time.lts.llm <- step.time.gap.ulm
  
  right.step.time.lts.75 <- as.numeric(quantile(right.step.time.lts, probs = 0.75))
  right.step.time.lts.25 <- as.numeric(quantile(right.step.time.lts, probs = 0.25))
  right.step.time.lts.iqr <- right.step.time.lts.75 - right.step.time.lts.25
  right.step.time.lts.ulm <- right.step.time.lts.75 + right.step.time.lts.iqr * 1.5
  right.step.time.lts.llm <- right.step.time.lts.25 - right.step.time.lts.iqr * 1.5
  if (right.step.time.lts.llm < step.time.gap.ulm) right.step.time.lts.llm <- step.time.gap.ulm
  
  step.time.df$rhythm <- "-"
  
  levels(step.time.df$rhythm) <- c("-", "long", "short", "left", "right", "shape")
  
  step.time.df$rhythm[!(step.time.df$state == "straight") & 
                        (step.time.df$step.leg == "left")] <- "left"
  step.time.df$rhythm[!(step.time.df$state == "straight") & 
                        (step.time.df$step.leg == "right")] <- "right"
  
  step.time.df$rhythm[((step.time.df$step.leg == "left") & 
                         (step.time.df$step.time.lt > left.step.time.lts.ulm)) | 
                        ((step.time.df$step.leg == "right") & 
                           (step.time.df$step.time.lt > right.step.time.lts.ulm))] <- "long"
  
  step.time.df$rhythm[((step.time.df$step.leg == "left") & 
                         (step.time.df$step.time.lt < left.step.time.lts.llm)) | 
                        ((step.time.df$step.leg == "right") & 
                           (step.time.df$step.time.lt < right.step.time.lts.llm))] <- "short"
  
  levels(gait.data.step$rhythm) <- c("-", "long", "short", "left", "right", "shape")
  
  if (any(step.time.df$rhythm == "long")) {
    
    long.step.time.df <- step.time.df[step.time.df$rhythm == "long", ]
    
    for (k in 1:nrow(long.step.time.df)) {
      
      long.step.time <- long.step.time.df[k, ]
      
      gait.data.step$rhythm[(gait.data.step$time >= long.step.time$head) & 
                              (gait.data.step$time <= long.step.time$tail)] <- "long"
      
    }
    
  }
  
  if (any(step.time.df$rhythm == "short")) {
    
    short.step.time.df <- step.time.df[step.time.df$rhythm == "short", ]
    
    for (k in 1:nrow(short.step.time.df)) {
      
      short.step.time <- short.step.time.df[k, ]
      
      gait.data.step$rhythm[(gait.data.step$time >= short.step.time$head) & 
                              (gait.data.step$time <= short.step.time$tail)] <- "short"
      
    }
    
  }
  
  # remove rhythm
  for (j in min(step.time.df$slice.id):max(step.time.df$slice.id)) {
    
    rhythm.step.time.df <- step.time.df[step.time.df$slice.id == j, ]
    
    if (!(nrow(rhythm.step.time.df) > 0)) next 
    
    if (!(any(rhythm.step.time.df$rhythm != "-"))) next
    
    if (!any(rhythm.step.time.df$state == "straight")) {
      
      remove.step.time.df <- rhythm.step.time.df[(rhythm.step.time.df$rhythm == "long") | 
                                                   (rhythm.step.time.df$rhythm == "short"), ]
      
      step.time.df <- step.time.df[!(step.time.df$head %in% remove.step.time.df$head), ]
      
      next
      
    } 
    
    remove.type <- ifelse(unique(rhythm.step.time.df$direction) == "forth", "after", "before")
    
    rhythm.step.time.df <- 
      switch (remove.type, 
              after = rhythm.step.time.df, 
              before = rhythm.step.time.df[order(rhythm.step.time.df$head, decreasing = TRUE), ])
    
    rhythm.step.time.df <- rhythm.step.time.df[-1, ]
    
    if (!any(rhythm.step.time.df$rhythm != "-")) next
    
    if (any(gait.data.step$step.id == 0) & 
        (j == start.step.time$slice.id)) {
      
      rhythm.step.time.df <- rhythm.step.time.df[-1, ]
      
      if (!any(rhythm.step.time.df$rhythm != "-")) next
      
    }
    
    rhythm.step.time <- head(rhythm.step.time.df[rhythm.step.time.df$rhythm != "-", ], n = 1)
    
    remove.step.time.df <- 
      switch (remove.type, 
              after = rhythm.step.time.df[rhythm.step.time.df$head >= rhythm.step.time$head, ], 
              before = rhythm.step.time.df[rhythm.step.time.df$tail <= rhythm.step.time$tail, ])
    
    step.time.df <- step.time.df[!(step.time.df$head %in% remove.step.time.df$head), ]
    
    if (!(nrow(remove.step.time.df) > 1)) next 
    
    remove.step.time.df <- remove.step.time.df[-1, ]
    
    remove.step.time.df$rhythm <- remove.step.time.df$step.leg
    
    for (k in 1:nrow(remove.step.time.df)) {
      
      remove.step.time <- remove.step.time.df[k, ]
      
      gait.data.step$rhythm[(gait.data.step$time >= remove.step.time$head) & 
                              (gait.data.step$time <= remove.step.time$tail)] <- remove.step.time$rhythm
      
    }
    
  }
  
  # check shape 
  for (j in min(step.time.df$slice.id):max(step.time.df$slice.id)) {
    
    shape.step.time.df <- step.time.df[step.time.df$slice.id == j, ]
    
    if (!(nrow(shape.step.time.df) > 0)) next
    
    if (!any(shape.step.time.df$state == "straight")) next 
    
    shape.step.time.df <- shape.step.time.df[(shape.step.time.df$head == head(shape.step.time.df$head, n = 1)) | 
                                               (shape.step.time.df$head == tail(shape.step.time.df$head, n = 1)), ]
    
    if (any(gait.data.step$step.id == 0) & 
        (j == start.step.time$slice.id)) shape.step.time.df <- shape.step.time.df[shape.step.time.df$head != start.step.time$head, ]
    
    if (!(nrow(shape.step.time.df) > 0)) next 
    
    for (k in 1:nrow(shape.step.time.df)) {
      
      shape.step.time <- shape.step.time.df[k, ]
      
      if (shape.step.time$rhythm == "short") {
        
        step.time.df <- step.time.df[step.time.df$head != shape.step.time$head, ]
        
        next
        
      }
      
      shape.step <- slice[(slice$time >= shape.step.time$head) & 
                            (slice$time <= shape.step.time$tail), ]
      
      shape.step.leg <- as.character(shape.step.time$step.leg)
      
      shape.step.ddt.adj.exm.time <- 
        switch (shape.step.leg, 
                left = min(shape.step$time[which.max(shape.step$ddt.adj)]), 
                right = min(shape.step$time[which.min(shape.step$ddt.adj)]))
      
      shape.step.time.75 <- as.numeric(quantile(shape.step$time, probs = 0.75))
      shape.step.time.25 <- as.numeric(quantile(shape.step$time, probs = 0.25))
      
      if ((shape.step.ddt.adj.exm.time > shape.step.time.75) | 
          (shape.step.ddt.adj.exm.time < shape.step.time.25)) {
        
        step.time.df <- step.time.df[step.time.df$head != shape.step.time$head, ]
        
        gait.data.step$rhythm[(gait.data.step$time >= shape.step.time$head) & 
                                (gait.data.step$time <= shape.step.time$tail)] <- "shape"
        
      } 
      
    }
    
  }
  
  MsgGait(data.id = data.id, gait.data = step.time.df, msg.type = "no.step")
  
  # assign step id
  for (k in 1:nrow(step.time.df)) {
    
    step.time <- step.time.df[k, ]
    
    step.time.leg <- as.character(step.time$step.leg)
    
    switch (step.time.leg, 
            left = {
              
              gait.data.step$step.id[(gait.data.step$time >= step.time$head) & 
                                       (gait.data.step$time <= step.time$tail)] <- k
              
            }, 
            right = {
              
              gait.data.step$step.id[(gait.data.step$time >= step.time$head) & 
                                       (gait.data.step$time <= step.time$tail)] <- k
              
            })
    
  }
  
  # assign step leg
  levels(gait.data.step$step.leg) <- c("-", "left", "right")
  gait.data.step$step.leg[gait.data.step$step.id > 0] <- gait.data.step$ddt.adj.leg[gait.data.step$step.id > 0]
  
  return (gait.data.step)
  
}

StrideGait <- function (data.id, gait.data.step) {
  # Calculate stride length, width, and duration,  
  # and output table and plot of stride data. 
  #
  # Args:
  #   data.id: id of step data (yyyy-mm-dd-n-n).
  #   gait.data.step: step data.
  #                    
  # Returns: 
  #   stride data.
  
  gait.data.stride <- data.frame(gait.data.step, 
                                 left.stance = -1, 
                                 right.stance = -1,
                                 left.stride.lt = -1, 
                                 right.stride.lt = -1, 
                                 left.stride.wt = -1, 
                                 right.stride.wt = -1, 
                                 left.stride.t = -1,
                                 right.stride.t = -1, 
                                 turn = "-")
  
  # extract stance
  slice.step <- gait.data.step[gait.data.step$step.id > 0, ]
  
  for (k in 1:max(slice.step$step.id)) {
    
    stance.step <- slice.step[slice.step$step.id == k, ]
    
    stance.step.leg <- as.character(unique(stance.step$step.leg))
    
    stance.time <- 
      switch (stance.step.leg, 
              left = stance.step$time[min(which.max(stance.step$ddt.adj))], 
              right = stance.step$time[min(which.min(stance.step$ddt.adj))])
    
    switch (stance.step.leg, 
            left = {
              gait.data.stride$left.stance[gait.data.stride$time == stance.time] <- k
            }, 
            right = {
              gait.data.stride$right.stance[gait.data.stride$time == stance.time] <- k
            })
    
  }
  
  # calculate stride length & width & duration
  straight.slice.step <- gait.data.stride[(gait.data.stride$state == "straight") & 
                                            (gait.data.stride$step.id > 0), ]
  
  for (j in 1:max(straight.slice.step$slice.id)) {
    
    stride.slice <- straight.slice.step[straight.slice.step$slice.id == j, ]
    
    if (!(nrow(stride.slice) > 0)) next
    
    left.stance <- stride.slice[stride.slice$left.stance > 0, ]
    right.stance <- stride.slice[stride.slice$right.stance > 0, ]
    
    if (nrow(left.stance) > 1) {
      
      left.stance.first <- head(left.stance$left.stance, n = 1)
      
      gait.data.stride$left.stride.lt[(gait.data.stride$slice.id == j) & 
                                        (gait.data.stride$left.stance > left.stance.first)] <- 
        left.stance$left.dt.inverse[-1] - left.stance$left.dt.inverse[-nrow(left.stance)]
      
      gait.data.stride$left.stride.wt[(gait.data.stride$slice.id == j) & 
                                        (gait.data.stride$left.stance > left.stance.first)] <- 
        left.stance$wt[-1]
      
      gait.data.stride$left.stride.t[(gait.data.stride$slice.id == j) & 
                                       (gait.data.stride$left.stance > left.stance.first)] <- 
        left.stance$time[-1] - left.stance$time[-nrow(left.stance)]
      
    }
    
    if (nrow(right.stance) > 1) {
      
      right.stance.first <- head(right.stance$right.stance, n = 1)
      
      gait.data.stride$right.stride.lt[(gait.data.stride$slice.id == j) & 
                                         (gait.data.stride$right.stance > right.stance.first)] <- 
        right.stance$right.dt.inverse[-1] - right.stance$right.dt.inverse[-nrow(right.stance)]
      
      gait.data.stride$right.stride.wt[(gait.data.stride$slice.id == j) & 
                                         (gait.data.stride$right.stance > right.stance.first)] <- 
        right.stance$wt[-1]
      
      gait.data.stride$right.stride.t[(gait.data.stride$slice.id == j) & 
                                        (gait.data.stride$right.stance > right.stance.first)] <- 
        right.stance$time[-1] - right.stance$time[-nrow(right.stance)]
      
    }
    
  }
  
  MsgGait(data.id = data.id, gait.data = gait.data.stride, msg.type = "no.stride")
  
  # calculate initiation stride length & width & duration
  stand.step <- gait.data.stride[gait.data.stride$step.id == 0, ]
  
  if (nrow(stand.step) > 0) {
    
    stand.slice.id <- max(stand.step$slice.id)
    
    start.stance <- straight.slice.step[(straight.slice.step$slice.id == stand.slice.id) & 
                                          ((straight.slice.step$left.stance > 0) | 
                                             (straight.slice.step$right.stance > 0)), ]
    
    if (nrow(start.stance) > 0) {
      
      left.start.stance <- start.stance[start.stance$left.stance > 0, ]
      right.start.stance <- start.stance[start.stance$right.stance > 0, ]
      
      if (nrow(left.start.stance) > 0) {
        
        left.start.stance <- left.start.stance[which.min(left.start.stance$left.stance), ]
        
        gait.data.stride$left.stance[1] <- 0
        
        gait.data.stride$left.stride.lt[gait.data.stride$left.stance == left.start.stance$left.stance] <- 
          left.start.stance$left.dt.inverse - median(stand.step$left.dt.inverse)
        
        gait.data.stride$left.stride.wt[gait.data.stride$left.stance == left.start.stance$left.stance] <- 
          left.start.stance$wt
        
        gait.data.stride$left.stride.t[gait.data.stride$left.stance == left.start.stance$left.stance] <- 
          left.start.stance$time - max(stand.step$time)
        
      }
      
      if (nrow(right.start.stance) > 0) {
        
        right.start.stance <- right.start.stance[which.min(right.start.stance$right.stance), ]
        
        gait.data.stride$right.stance[1] <- 0
        
        gait.data.stride$right.stride.lt[gait.data.stride$right.stance == right.start.stance$right.stance] <- 
          right.start.stance$right.dt.inverse - median(stand.step$right.dt.inverse)
        
        gait.data.stride$right.stride.wt[gait.data.stride$right.stance == right.start.stance$right.stance] <- 
          right.start.stance$wt
        
        gait.data.stride$right.stride.t[gait.data.stride$right.stance == right.start.stance$right.stance] <- 
          right.start.stance$time - max(stand.step$time)
        
      }
      
    }
    
  }
  
  # calculate turning duration and side
  turn <- gait.data.stride[gait.data.stride$state == "turn", ]
  
  turn.head <- min(turn$time)
  turn.tail <- max(turn$time)
  
  straight.step <- gait.data.stride[(gait.data.stride$state == "straight") & 
                                      ((gait.data.stride$step.id > 0) | 
                                         (gait.data.stride$rhythm == "left") | 
                                         (gait.data.stride$rhythm == "right")), ]
  
  left.stance.ddt.adj <- straight.step$ddt.adj[straight.step$left.stance > 0]
  right.stance.ddt.adj <- straight.step$ddt.adj[straight.step$right.stance > 0]
  
  left.stance.ddt.adj.75 <- as.numeric(quantile(left.stance.ddt.adj, probs = 0.75))
  left.stance.ddt.adj.25 <- as.numeric(quantile(left.stance.ddt.adj, probs = 0.25))
  left.stance.ddt.adj.iqr <- left.stance.ddt.adj.75 - left.stance.ddt.adj.25
  left.stance.ddt.adj.llm <- left.stance.ddt.adj.25 - left.stance.ddt.adj.iqr * 1.5
  
  right.stance.ddt.adj.75 <- as.numeric(quantile(right.stance.ddt.adj, probs = 0.75))
  right.stance.ddt.adj.25 <- as.numeric(quantile(right.stance.ddt.adj, probs = 0.25))
  right.stance.ddt.adj.iqr <- right.stance.ddt.adj.75 - right.stance.ddt.adj.25
  right.stance.ddt.adj.ulm <- right.stance.ddt.adj.75 + right.stance.ddt.adj.iqr * 1.5
  
  forth.straight.step <- straight.step[straight.step$direction == "forth", ]
  back.straight.step <- straight.step[straight.step$direction == "back", ]
  
  if (nrow(forth.straight.step) > 0) {
    turn.head <- min(gait.data.stride$time[which(gait.data.stride$time > max(forth.straight.step$time))])
    
  } else turn.head <- min(gait.data.stride$time[(gait.data.stride$direction == "forth") & 
                                                  (gait.data.stride$state == "buffer")])
  
  if (nrow(back.straight.step) > 0) {
    turn.tail <- max(gait.data.stride$time[which(gait.data.stride$time < min(back.straight.step$time))])
    
  } else turn.tail <- max(gait.data.stride$time[(gait.data.stride$direction == "back") & 
                                                  (gait.data.stride$state == "buffer")])
  
  turn <- gait.data.stride[(gait.data.stride$time >= turn.head) & 
                             (gait.data.stride$time <= turn.tail), ]
  
  buffer <- turn[turn$state != "turn", ]
  
  if (nrow(buffer) > 0) {
    
    buffer.step.time.indexes <- which(buffer$ddt.adj.leg[-1] != buffer$ddt.adj.leg[-nrow(buffer)])
    
    buffer.step.time.indexes <- c(buffer.step.time.indexes, 
                                  max(which(buffer$direction == "forth")))
    
    if (length(unique(buffer$slice.id[buffer$state != "straight"])) > 1) {
      
      buffer.slice.ids <- unique(buffer$slice.id[buffer$state != "straight"])
      
      for (j in 1:length(buffer.slice.ids)) {
        
        buffer.slice.id <- buffer.slice.ids[j]
        
        buffer.step.time.indexes <- c(buffer.step.time.indexes, 
                                      max(which(buffer$slice.id == buffer.slice.id)))
        
      }
      
    }
    
    buffer.step.time.indexes <- buffer.step.time.indexes[buffer.step.time.indexes != max(which(buffer$direction == "back"))]
    
    buffer.step.time.indexes <- buffer.step.time.indexes[buffer.step.time.indexes != nrow(buffer)] 
    
    if (length(buffer.step.time.indexes) > 0) {
      
      buffer.step.time.indexes <- unique(buffer.step.time.indexes)
      
      buffer.step.time.indexes <- sort(buffer.step.time.indexes)
      
      buffer.step.time.df <- data.frame(head = c(head(buffer$time, n = 1), 
                                                 buffer$time[buffer.step.time.indexes + 1]), 
                                        tail = c(buffer$time[buffer.step.time.indexes], 
                                                 tail(buffer$time, n = 1)), 
                                        direction = buffer$direction[c(buffer.step.time.indexes, nrow(buffer))], 
                                        step.leg = buffer$ddt.adj.leg[c(buffer.step.time.indexes, nrow(buffer))])
      
      forth.buffer.step.time.df <- buffer.step.time.df[buffer.step.time.df$direction == "forth", ]
      back.buffer.step.time.df <- buffer.step.time.df[buffer.step.time.df$direction == "back", ]
      
      if (nrow(forth.buffer.step.time.df) > 0) {
        
        for (k in 1:nrow(forth.buffer.step.time.df)) {
          
          forth.buffer.step.time <- forth.buffer.step.time.df[k, ]
          
          forth.buffer.step <- gait.data.stride[(gait.data.stride$time >= forth.buffer.step.time$head) & 
                                                  (gait.data.stride$time <= forth.buffer.step.time$tail), ]
          
          forth.buffer.step.time.75 <- as.numeric(quantile(forth.buffer.step$time, probs = 0.75))
          forth.buffer.step.time.25 <- as.numeric(quantile(forth.buffer.step$time, probs = 0.25))
          
          forth.buffer.step.50 <- forth.buffer.step[(forth.buffer.step$time >= forth.buffer.step.time.25) & 
                                                      (forth.buffer.step$time <= forth.buffer.step.time.75), ]
          
          if (!(nrow(forth.buffer.step.50) > 0)) next
          
          forth.buffer.step.leg <- as.character(forth.buffer.step.time$step.leg)
          
          if (switch (forth.buffer.step.leg, 
                      left = max(forth.buffer.step.50$ddt.adj) < left.stance.ddt.adj.llm, 
                      right = min(forth.buffer.step.50$ddt.adj) > right.stance.ddt.adj.ulm)) break 
          
          if (any(turn$time > forth.buffer.step.time$tail)) {
            
            turn.head <- min(turn$time[which(turn$time > forth.buffer.step.time$tail)])
            
            turn <- turn[turn$time >= turn.head, ]
            
          }
          
        }
        
      }
      
      if (nrow(back.buffer.step.time.df) > 0) {
        
        for (k in 1:nrow(back.buffer.step.time.df)) {
          
          back.buffer.step.time <- back.buffer.step.time.df[k, ]
          
          back.buffer.step <- gait.data.stride[(gait.data.stride$time >= back.buffer.step.time$head) & 
                                                 (gait.data.stride$time <= back.buffer.step.time$tail), ]
          
          back.buffer.step.time.75 <- as.numeric(quantile(back.buffer.step$time, probs = 0.75))
          back.buffer.step.time.25 <- as.numeric(quantile(back.buffer.step$time, probs = 0.25))
          
          back.buffer.step.50 <- back.buffer.step[(back.buffer.step$time >= back.buffer.step.time.25) & 
                                                    (back.buffer.step$time <= back.buffer.step.time.75), ]
          
          if (!(nrow(back.buffer.step.50) > 0)) next 
          
          back.buffer.step.leg <- as.character(back.buffer.step.time$step.leg)
          
          if (switch (back.buffer.step.leg, 
                      left = max(back.buffer.step.50$ddt.adj) < left.stance.ddt.adj.llm, 
                      right = min(back.buffer.step.50$ddt.adj) > right.stance.ddt.adj.ulm)) break 
          
          if (any(turn$time < back.buffer.step.time$head)) {
            
            turn.tail <- max(turn$time[which(turn$time < back.buffer.step.time$head)])
            
            turn <- turn[turn$time <= turn.tail, ]
            
          }
          
        }
        
      } 
      
    }
    
  }
  
  levels(gait.data.stride$turn) <- c("-", "turn", "left", "right")
  gait.data.stride$turn[(gait.data.stride$time >= turn.head) & 
                          (gait.data.stride$time <= turn.tail)] <- "turn"
  
  left.turn.x.sft <- abs(max(turn$left.x.smooth) - min(turn$left.x.smooth))
  right.turn.x.sft <- abs(max(turn$right.x.smooth) - min(turn$right.x.smooth))
  
  gait.data.stride$turn[gait.data.stride$turn == "turn"] <- ifelse(left.turn.x.sft < right.turn.x.sft, "left", "right")
  
  # write stride
  IOGait(io.type = "write", 
         gait.path = FilePathGait(path.type = "write", data.id = data.id, gait.data.type = "stride"), 
         gait.data = gait.data.stride)
  
  return (gait.data.stride)
  
}

SummaryGait <- function (pt.id, data.ids, gait.data.ls) {
  # Summary for stride data, 
  # and output table of summary data. 
  #
  # Args:
  #   pt.id: id of patient (yyyy-mm-dd-n). 
  #   data.ids: ids of stride data (yyyy-mm-dd-n-n).
  #   gait.data.ls: list of stride data.
  
  data.n <- length(data.ids)
  
  gait.data.summary <- data.frame(data.id = data.ids, 
                                  left.size = -1, 
                                  left.stride.lt.mu = -1, 
                                  left.stride.lt.sd = -1, 
                                  left.stride.wt.mu = -1, 
                                  left.stride.wt.sd = -1, 
                                  left.stride.t.mu = -1, 
                                  left.stride.t.sd = -1, 
                                  right.size = -1, 
                                  right.stride.lt.mu = -1, 
                                  right.stride.lt.sd = -1, 
                                  right.stride.wt.mu = -1, 
                                  right.stride.wt.sd = -1, 
                                  right.stride.t.mu = -1, 
                                  right.stride.t.sd = -1, 
                                  start.leg = "-", 
                                  left.start.lt = -1, 
                                  left.start.t = -1, 
                                  right.start.lt = -1, 
                                  right.start.t = -1, 
                                  velocity = -1, 
                                  left.velocity = -1, 
                                  right.velocity = -1, 
                                  cadence = -1, 
                                  left.cadence = -1, 
                                  right.cadence = -1, 
                                  turn.t = -1, 
                                  turn.side = "-", 
                                  left.turn.t = -1, 
                                  right.turn.t = -1)
  
  levels(gait.data.summary$start.leg) <- c("-", "left", "right", "both")
  levels(gait.data.summary$turn.side) <- c("-", "left", "right", "both")
  
  left.stride.df <- data.frame(lt = numeric(), 
                               wt = numeric(), 
                               t = numeric(), 
                               data.id = character(), 
                               stringsAsFactors = FALSE)
  
  right.stride.df <- data.frame(lt = numeric(), 
                                wt = numeric(), 
                                t = numeric(), 
                                data.id = character(), 
                                stringsAsFactors = FALSE)
  
  for (i in 1:data.n) {
    
    data.id <- data.ids[i]
    
    gait.data.stride <- gait.data.ls[[i]]
    
    # calculate summary of stride length & width & duration
    left.stride <- gait.data.stride[gait.data.stride$left.stride.lt > 0, ]
    right.stride <- gait.data.stride[gait.data.stride$right.stride.lt > 0, ]
    
    if (any(gait.data.stride$left.stance == 0)) left.stride <- tail(left.stride, n = -1)
    if (any(gait.data.stride$right.stance == 0)) right.stride <- tail(right.stride, n = -1)
    
    if (nrow(left.stride) > 0) {
      
      gait.data.summary$left.size[i] <- nrow(left.stride)
      
      gait.data.summary$left.stride.lt.mu[i] <- mean(left.stride$left.stride.lt)
      gait.data.summary$left.stride.lt.sd[i] <- sd(left.stride$left.stride.lt)
      gait.data.summary$left.stride.wt.mu[i] <- mean(left.stride$left.stride.wt)
      gait.data.summary$left.stride.wt.sd[i] <- sd(left.stride$left.stride.wt)
      gait.data.summary$left.stride.t.mu[i] <- mean(left.stride$left.stride.t)
      gait.data.summary$left.stride.t.sd[i] <- sd(left.stride$left.stride.t)
      
      left.stride.df <- data.frame(lt = c(left.stride.df$lt, left.stride$left.stride.lt), 
                                   wt = c(left.stride.df$wt, left.stride$left.stride.wt), 
                                   t = c(left.stride.df$t, left.stride$left.stride.t), 
                                   data.id = c(left.stride.df$data.id, rep(data.id, times = nrow(left.stride))), 
                                   stringsAsFactors = FALSE)
      
    } else gait.data.summary$left.size[i] <- 0
    
    if (nrow(right.stride) > 0) {
      
      gait.data.summary$right.size[i] <- nrow(right.stride)
      
      gait.data.summary$right.stride.lt.mu[i] <- mean(right.stride$right.stride.lt)
      gait.data.summary$right.stride.lt.sd[i] <- sd(right.stride$right.stride.lt)
      gait.data.summary$right.stride.wt.mu[i] <- mean(right.stride$right.stride.wt)
      gait.data.summary$right.stride.wt.sd[i] <- sd(right.stride$right.stride.wt)
      gait.data.summary$right.stride.t.mu[i] <- mean(right.stride$right.stride.t)
      gait.data.summary$right.stride.t.sd[i] <- sd(right.stride$right.stride.t)
      
      right.stride.df <- data.frame(lt = c(right.stride.df$lt, right.stride$right.stride.lt), 
                                    wt = c(right.stride.df$wt, right.stride$right.stride.wt), 
                                    t = c(right.stride.df$t, right.stride$right.stride.t), 
                                    data.id = c(right.stride.df$data.id, rep(data.id, times = nrow(right.stride))), 
                                    stringsAsFactors = FALSE)
      
    } else gait.data.summary$right.size[i] <- 0
    
    # calculate summary of initiation stride length & width & duration
    stand.stance <- gait.data.stride[(gait.data.stride$left.stance == 0) | 
                                       (gait.data.stride$right.stance == 0), ]
    
    if (nrow(stand.stance) > 0) {
      
      gait.data.summary$start.leg[i] <- gait.data.stride$step.leg[(gait.data.stride$left.stance == 1) | 
                                                                    (gait.data.stride$right.stance == 1)]
      
      if (any(gait.data.stride$left.stance == 0)) {
        
        left.start.stride <- head(gait.data.stride[gait.data.stride$left.stride.lt > 0, ], n = 1)
        
        gait.data.summary$left.start.lt[i] <- left.start.stride$left.stride.lt
        gait.data.summary$left.start.t[i] <- left.start.stride$left.stride.t
        
      }
      
      if (any(gait.data.stride$right.stance == 0)) {
        
        right.start.stride <- head(gait.data.stride[gait.data.stride$right.stride.lt > 0, ], n = 1)
        
        gait.data.summary$right.start.lt[i] <- right.start.stride$right.stride.lt
        gait.data.summary$right.start.t[i] <- right.start.stride$right.stride.t
        
      }
      
    }
    
    # calculate velocity and cadence
    if (nrow(left.stride) > 0) {
      
      gait.data.summary$left.velocity[i] <- 
        sum(left.stride$left.stride.lt) / sum(left.stride$left.stride.t)
      
      gait.data.summary$left.cadence[i] <- 
        (gait.data.summary$left.size[i] / sum(left.stride$left.stride.t)) * 1000 * 60
      
      gait.data.summary$velocity[i] <- gait.data.summary$left.velocity[i]
      gait.data.summary$cadence[i] <- gait.data.summary$left.cadence[i]
      
    }
    
    if (nrow(right.stride) > 0) {
      
      gait.data.summary$right.velocity[i] <- 
        sum(right.stride$right.stride.lt) / sum(right.stride$right.stride.t)
      
      gait.data.summary$right.cadence[i] <- 
        (gait.data.summary$right.size[i] / sum(right.stride$right.stride.t)) * 1000 * 60
      
      gait.data.summary$velocity[i] <- gait.data.summary$right.velocity[i]
      gait.data.summary$cadence[i] <- gait.data.summary$right.cadence[i]
      
    }
    
    if ((nrow(left.stride) > 0) & 
        (nrow(right.stride) > 0)) {
      
      gait.data.summary$velocity[i] <- 
        sum(left.stride$left.stride.lt, right.stride$right.stride.lt) / 
        sum(left.stride$left.stride.t, right.stride$right.stride.t)
      
      gait.data.summary$cadence[i] <- 
        (sum(gait.data.summary$left.size[i], gait.data.summary$right.size[i]) / 
           sum(left.stride$left.stride.t, right.stride$right.stride.t)) * 1000 * 60
      
    }
    
    # calculate turning duration
    turn <- gait.data.stride[gait.data.stride$turn != "-", ]
    
    gait.data.summary$turn.t[i] <- max(turn$time) - min(turn$time)
    
    # extract turning side
    gait.data.summary$turn.side[i] <- unique(turn$turn)
    
    if (gait.data.summary$turn.side[i] == "left") gait.data.summary$left.turn.t[i] <- gait.data.summary$turn.t[i]
    if (gait.data.summary$turn.side[i] == "right") gait.data.summary$right.turn.t[i] <- gait.data.summary$turn.t[i]
    
  }
  
  # write stride left
  IOGait(io.type = "write", 
         gait.path = FilePathGait(path.type = "write", data.id = pt.id, gait.data.type = "summary", gait.data.leg = "left"), 
         gait.data = left.stride.df)
  
  # write stride right
  IOGait(io.type = "write", 
         gait.path = FilePathGait(path.type = "write", data.id = pt.id, gait.data.type = "summary", gait.data.leg = "right"), 
         gait.data = right.stride.df)
  
  # calculate total summary
  pt.gait.data.summary <- data.frame(data.id = "total", 
                                     left.size = -1, 
                                     left.stride.lt.mu = -1, 
                                     left.stride.lt.sd = -1, 
                                     left.stride.wt.mu = -1, 
                                     left.stride.wt.sd = -1, 
                                     left.stride.t.mu = -1, 
                                     left.stride.t.sd = -1, 
                                     right.size = -1, 
                                     right.stride.lt.mu = -1, 
                                     right.stride.lt.sd = -1, 
                                     right.stride.wt.mu = -1, 
                                     right.stride.wt.sd = -1, 
                                     right.stride.t.mu = -1, 
                                     right.stride.t.sd = -1, 
                                     start.leg = "-", 
                                     left.start.lt = -1, 
                                     left.start.t = -1, 
                                     right.start.lt = -1, 
                                     right.start.t = -1, 
                                     velocity = -1, 
                                     left.velocity = -1, 
                                     right.velocity = -1, 
                                     cadence = -1, 
                                     left.cadence = -1, 
                                     right.cadence = -1, 
                                     turn.t = -1, 
                                     turn.side = "-", 
                                     left.turn.t = -1, 
                                     right.turn.t = -1)
  
  levels(pt.gait.data.summary$start.leg) <- c("-", "left", "right", "both")
  levels(pt.gait.data.summary$turn.side) <- c("-", "left", "right", "both")
  
  left.summary <- gait.data.summary[gait.data.summary$left.size > 0, ]
  right.summary <- gait.data.summary[gait.data.summary$right.size > 0, ]
  
  pt.gait.data.summary$left.size <- sum(left.summary$left.size)
  pt.gait.data.summary$right.size <- sum(right.summary$right.size)
  
  pt.gait.data.summary$left.stride.lt.mu <- mean(left.stride.df$lt)
  pt.gait.data.summary$left.stride.lt.sd <- sd(left.stride.df$lt)
  pt.gait.data.summary$left.stride.wt.mu <- mean(left.stride.df$wt)
  pt.gait.data.summary$left.stride.wt.sd <- sd(left.stride.df$wt)
  pt.gait.data.summary$left.stride.t.mu <- mean(left.stride.df$t)
  pt.gait.data.summary$left.stride.t.sd <- sd(left.stride.df$t)
  
  pt.gait.data.summary$right.stride.lt.mu <- mean(right.stride.df$lt)
  pt.gait.data.summary$right.stride.lt.sd <- sd(right.stride.df$lt)
  pt.gait.data.summary$right.stride.wt.mu <- mean(right.stride.df$wt)
  pt.gait.data.summary$right.stride.wt.sd <- sd(right.stride.df$wt)
  pt.gait.data.summary$right.stride.t.mu <- mean(right.stride.df$t)
  pt.gait.data.summary$right.stride.t.sd <- sd(right.stride.df$t)
  
  left.start.summary <- gait.data.summary[gait.data.summary$start.leg == "left", ]
  right.start.summary <- gait.data.summary[gait.data.summary$start.leg == "right", ]
  
  if (nrow(left.start.summary) > 0) {
    
    pt.gait.data.summary$start.leg <- "left"
    pt.gait.data.summary$left.start.lt <- mean(left.start.summary$left.start.lt)
    pt.gait.data.summary$left.start.t <- mean(left.start.summary$left.start.t)
    
  }
  
  if (nrow(right.start.summary) > 0) {
    
    pt.gait.data.summary$start.leg <- "right"
    pt.gait.data.summary$right.start.lt <- mean(right.start.summary$right.start.lt)
    pt.gait.data.summary$right.start.t <- mean(right.start.summary$right.start.t)
    
  }
  
  if ((nrow(left.start.summary) > 0) & 
      (nrow(right.start.summary) > 0)) pt.gait.data.summary$start.leg <- "both"
  
  pt.gait.data.summary$velocity <- 
    sum(left.stride.df$lt, right.stride.df$lt) / 
    sum(left.stride.df$t, right.stride.df$t)
  
  pt.gait.data.summary$left.velocity <- 
    sum(left.stride.df$lt) / sum(left.stride.df$t)
  
  pt.gait.data.summary$right.velocity <- 
    sum(right.stride.df$lt) / sum(right.stride.df$t)
  
  pt.gait.data.summary$cadence <- 
    sum(pt.gait.data.summary$left.size, pt.gait.data.summary$right.size) / 
    sum(left.stride.df$t, right.stride.df$t) * 1000 * 60
  
  pt.gait.data.summary$left.cadence <- 
    (pt.gait.data.summary$left.size / sum(left.stride.df$t)) * 1000 * 60
  
  pt.gait.data.summary$right.cadence <- 
    (pt.gait.data.summary$right.size / sum(right.stride.df$t)) * 1000 * 60
  
  pt.gait.data.summary$turn.t <- 
    sum(gait.data.summary$turn.t) / data.n
  
  left.turn <- gait.data.summary[gait.data.summary$turn.side == "left", ]
  right.turn <- gait.data.summary[gait.data.summary$turn.side == "right", ]
  
  if (nrow(left.turn) > 0) {
    
    pt.gait.data.summary$turn.side <- "left"
    
    pt.gait.data.summary$left.turn.t <- 
      sum(left.turn$turn.t) / nrow(left.turn)
    
  }
  
  if (nrow(right.turn) > 0) {
    
    pt.gait.data.summary$turn.side <- "right"
    
    pt.gait.data.summary$right.turn.t <- 
      sum(right.turn$turn.t) / nrow(right.turn)
    
  }
  
  if ((nrow(left.turn) > 0) & 
      (nrow(right.turn) > 0)) pt.gait.data.summary$turn.side <- "both"
  
  MsgGait(data.id = pt.id, gait.data = pt.gait.data.summary, msg.type = "no.summary")
  
  gait.data.summary <- rbind(pt.gait.data.summary, gait.data.summary)
  
  # write summary
  IOGait(io.type = "write", 
         gait.path = FilePathGait(path.type = "write", data.id = pt.id, gait.data.type = "summary", gait.data.leg = "both"), 
         gait.data = gait.data.summary)
  
}

# setwd()  # ./zGait/
#if (basename(getwd()) != "zGait") SetWDGait("set.back")


# ZED setting -------------------------------------------------------------

frame.per.sec <- 30 
frame.time.gap <- 1000/frame.per.sec  # msec

# batch calculation -------------------------------------------------------

# individual
# batch.info <- data.frame(yyyy = "2019",
#                          mm = "02",
#                          dd = "13",
#                          id = c(1),
#                          round.n = 1,
#                          note = "")

#batch.path <- file.choose()
# Rscript gait_batch.R /Users/kaminyou/Desktop/publication/zGaitSetUp/zGait/input/20210401.csv
# Rscript gait_batch.R /Users/kaminyou/Desktop/publication/zGaitSetUp/zGait/input/20010101.csv
args <- commandArgs(trailingOnly = TRUE)
if (length(args) == 0) {
  stop("No batch path provided.")
}
batch.path <- args[1]
print("Use path")
print(batch.path)
batch.id <- gsub("\\.csv", "", basename(batch.path))

batch.info <- read.csv(batch.path,  # ./input/batch_info.csv
                       col.names = c("yyyy", "mm", "dd", "id", "round.n", "note"),
                       colClasses = "character")

batch.info$mm[nchar(batch.info$mm) == 1] <- paste("0", batch.info$mm[nchar(batch.info$mm) == 1], sep = "")
batch.info$dd[nchar(batch.info$dd) == 1] <- paste("0", batch.info$dd[nchar(batch.info$dd) == 1], sep = "")

batch <- BatchNoteGait(batch.info = batch.info, batch.id = batch.id)

pts.n <- nrow(batch)

batch.cursor <- 0

while (batch.cursor < pts.n) {
  
  batch.cursor <- batch.cursor + 1
  
  pt.info <- batch[batch.cursor, ]
  
  pt.id <- pt.info$pt.id
  
  pt.info.round.ids <- unlist(strsplit(as.character(pt.info$round.ids), split = ","))
  
  data.ids <- paste(pt.id, pt.info.round.ids, sep = "-")
  
  SetWDGait(set.dir.type = "set", pt.id)
  
  data.n = length(data.ids)
  
  gait.data.ls <- vector("list", length = data.n)
  
  for (i in 1:data.n) {
    
    data.id <- data.ids[i]
    
    gait.data <- RawCleanGait(data.id = data.id)
    gait.data <- SmoothGait(data.id = data.id, gait.data.clean = gait.data, smooth.window = 5)
    gait.data <- stateGait(data.id = data.id, gait.data.smooth = gait.data, buffer.window = 3)
    gait.data <- SliceGait(data.id = data.id, gait.data.state = gait.data, time.gap.ulm = frame.time.gap * 7, slice.time.lt.llm = frame.time.gap * 8)
    gait.data <- StepGait(data.id = data.id, gait.data.slice = gait.data, runs.window = 3, step.time.gap.ulm = frame.time.gap * 2)
    gait.data <- StrideGait(data.id = data.id, gait.data.step = gait.data)
    
    cat(data.id, "\n")
    
    gait.data.ls[[i]] <- gait.data
    
  }
  
  SummaryGait(pt.id = pt.id, data.ids = data.ids, gait.data.ls = gait.data.ls)
  
  SetWDGait(set.dir.type = "set.back")
  
  if (batch.cursor <= pts.n) cat("\n")
  
}
